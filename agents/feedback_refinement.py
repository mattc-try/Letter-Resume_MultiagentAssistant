# MIT License
# 
# Copyright (c) 2024 mattc-try (GitHub)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

from textblob import TextBlob
import textstat
import spacy
from transformers import pipeline
from crewai import Agent, Task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

class FeedbackRefinement:
    """
    A class to evaluate and refine resumes or cover letters. This includes:
    - Grammar correction
    - Readability scoring
    - Sentiment analysis
    - Structural analysis
    - Generating refined content following feedback
    """
    def __init__(self):
        # Initialize transformer-based grammar correction pipeline
        self.grammar_corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1")
        
        # Load spaCy model for NLP tasks
        self.nlp = spacy.load('en_core_web_sm')

        self.scrape_tool = ScrapeWebsiteTool()

        self.feedback_compiling=self._create_feedback_compiling_agent()
        self.feedback_refinement=self._create_feedback_refinement_agent()
        self.resume_refiner=self._create_resume_refiner_agent()
        self.cover_letter_refiner=self._create_cover_letter_refiner_agent()


        self.feedback_generation_task=self._create_feedback_task()


    def evaluate_content(self, content, content_type="resume"):
        """
        Evaluate the given content (resume or cover letter) and return feedback.
        
        :param content: The text content of the resume or cover letter.
        :param content_type: Either "resume" or "cover_letter" to determine structural expectations.
        :return: A dictionary of feedback containing grammar, readability, sentiment, structure, tone, score, and recommendations.
        """
        feedback = {}

        # 1. Grammar and Spell Checking
        grammar_feedback = self.correct_grammar(content)
        feedback['grammar'] = grammar_feedback

        # 2. Readability Analysis using textstat
        readability_scores = {
            'flesch_reading_ease': textstat.flesch_reading_ease(content),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(content),
            'gunning_fog': textstat.gunning_fog(content),
            'smog_index': textstat.smog_index(content),
            'automated_readability_index': textstat.automated_readability_index(content),
            'coleman_liau_index': textstat.coleman_liau_index(content),
            'linsear_write_formula': textstat.linsear_write_formula(content),
            'dale_chall_readability_score': textstat.dale_chall_readability_score(content)
        }
        feedback['readability'] = readability_scores

        feedback['sentiment'] = self.assess_tone(content)

        # 4. Structural Analysis
        structure_feedback = self.analyze_structure(content, content_type)
        feedback['structure'] = structure_feedback

        # 6. Scoring and Score Explanation
        score, score_comment = self.calculate_score(feedback)
        feedback['score'] = score
        feedback['score_comment'] = score_comment

        # 7. Recommendations
        recommendations = self.generate_recommendations(feedback, content_type)
        feedback['recommendations'] = recommendations

        return feedback, feedback['score']

    def correct_grammar(self, content):
        """
        Correct grammar and spelling using a transformer-based model.
        """
        corrected = self.grammar_corrector(content, max_length=512, truncation=True)
        corrected_text = corrected[0]['generated_text']

        # Compare original and corrected text (simple heuristic)
        original_words = content.split()
        corrected_words = corrected_text.split()
        differences = sum(1 for o, c in zip(original_words, corrected_words) if o != c)
        
        errors = []
        for original, corrected_word in zip(original_words, corrected_words):
            if original != corrected_word:
                errors.append(f"Original: {original} --> Corrected: {corrected_word}")
        
        return {
            'error_count': differences,
            'errors': errors,
            'corrected_content': corrected_text
        }

    def analyze_structure(self, content, content_type):
        """
        Analyze the structure of the content based on whether it's a resume or cover letter.
        """
        if content_type == "resume":
            # Standard sections for a resume
            standard_sections = [
                'Contact Information',
                'Summary',
                'Work Experience',
                'Education',
                'Skills'
            ]
        else:
            # Standard sections for a cover letter
            # These are conceptual rather than strictly "sections," but we check for cues.
            standard_sections = [
                'Greeting',      # e.g. "Dear Hiring Manager,"
                'Introduction',  # Intro paragraph stating intent
                'Body',          # Main body paragraphs highlighting relevant skills/experience
                'Conclusion',    # Closing remarks, restating interest
                'Sign-off'       # e.g. "Sincerely, [Name]"
            ]

        doc = self.nlp(content)
        found_sections = set()

        for sent in doc.sents:
            sent_text_lower = sent.text.lower()
            for section in standard_sections:
                # For the cover letter, these sections are conceptual. We'll do basic keyword checks:
                if content_type == "cover_letter":
                    if section == 'Greeting' and ("dear" in sent_text_lower or "hello" in sent_text_lower):
                        found_sections.add('Greeting')
                    elif section == 'Introduction' and ("i am writing" in sent_text_lower or "interested in" in sent_text_lower):
                        found_sections.add('Introduction')
                    elif section == 'Body' and ("experience" in sent_text_lower or "skills" in sent_text_lower):
                        found_sections.add('Body')
                    elif section == 'Conclusion' and ("thank you" in sent_text_lower or "looking forward" in sent_text_lower):
                        found_sections.add('Conclusion')
                    elif section == 'Sign-off' and ("sincerely" in sent_text_lower or "best regards" in sent_text_lower):
                        found_sections.add('Sign-off')
                else:
                    # For resumes, look for actual section titles
                    if section.lower() in sent_text_lower:
                        found_sections.add(section)

        missing_sections = set(standard_sections) - found_sections

        return {
            'found_sections': list(found_sections),
            'missing_sections': list(missing_sections)
        }

    def assess_tone(self, content):
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity  # [-1.0, 1.0]
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            tone = 'Positive'
        elif polarity < -0.1:
            tone = 'Negative'
        else:
            tone = 'Neutral'

        return {
            'polarity': polarity,
            'tone': tone,
            'subjectivity': subjectivity
        }   

    def calculate_score(self, feedback):
        """
        A scoring mechanism combining grammar quality, readability (Flesch-Kincaid & Gunning Fog), and sentiment.
        Scores will be between 0 and 100. Less punitive to produce better scores.
        """
        # Start with a base score
        score = 100.0
        reasons = []

        # 1. Grammar Errors: Reduced Deduction Severity
        grammar_errors = feedback['grammar']['error_count']
        if grammar_errors > 0:
            penalty = grammar_errors * 0.5  # Reduce impact (0.5 points per error)
            if grammar_errors <= 2:  # Allow up to 2 errors with no penalty
                penalty = 0
            score -= penalty
            if penalty > 0:
                reasons.append(f"{grammar_errors} grammar/spelling error(s) reduced the score by {penalty:.2f} points.")


        # 3. Gunning Fog Index Adjustment
        gunning_fog = feedback['readability']['gunning_fog']
        if gunning_fog > 14:  # Target readability for professional documents
            diff = (gunning_fog - 14) * 0.75  # Lower the multiplier
            if diff > 3:  # Cap the maximum penalty at 3 points
                diff = 3
            score -= diff
            reasons.append(f"Complex sentence structure (Gunning Fog Index {gunning_fog:.2f}) reduced the score by {diff:.2f} points.")

        # 4. Sentiment Polarity: More Lenient Penalty
        polarity = feedback['sentiment']['polarity']
        if polarity < -0.3:  # Penalize only for strong negativity
            score -= 5  # Reduced penalty for very negative tone
            reasons.append("Strong negative tone reduced the score by 5 points.")

        # Bound the score between 0 and 100
        score = max(0, min(100, score))

        # Add default message if no deductions
        if not reasons:
            reasons.append("No major issues; score remained high.")

        # Combine score explanation
        score_comment = "Score Explanation: " + " ".join(reasons)

        return score, score_comment

    def generate_recommendations(self, feedback, content_type):
        recommendations = []

        # Grammar recommendations
        if feedback['grammar']['error_count'] > 0:
            recommendations.append("Consider reviewing grammar and spelling to reduce errors.")

        # Readability recommendations
        if feedback['readability']['flesch_kincaid_grade'] > 12:
            recommendations.append("Try simplifying the language to improve readability.")

        # Tone recommendations
        if feedback['sentiment']['tone'] == 'Negative':
            recommendations.append("Aim for a more positive or neutral tone to appeal to a broader audience.")

        # Structural recommendations
        missing_sections = feedback['structure']['missing_sections']
        if missing_sections:
            if content_type == "resume":
                recommendations.append("Consider adding the following resume sections: " + ", ".join(missing_sections))
            else:
                recommendations.append("Consider incorporating elements of a standard cover letter structure: " + ", ".join(missing_sections))

        if not recommendations:
            recommendations.append("Overall, the content looks good. Minor improvements can be made for clarity and tone.")

        return recommendations
    


    def _create_feedback_compiling_agent(self):
        return Agent(
            role="Feedback Compiler",
            goal="Aggregate and organize feedback from various sources to form a comprehensive overview.",
            tools=[self.scrape_tool],
            verbose=True,
            backstory=(
                "As a Feedback Compiler, you excel at gathering diverse feedback from multiple channels, "
                "ensuring that all insights are meticulously organized and ready for further analysis and refinement."
            )
        )
    
    def _create_feedback_refinement_agent(self):
        return Agent(
            role="Feedback Refiner",
            goal="Enhance and clarify the compiled feedback to ensure it is actionable and precise.",
            tools=[],
            verbose=True,
            backstory=(
                "As a Feedback Refiner, your attention to detail ensures that all compiled feedback is polished, "
                "eliminating ambiguities and enhancing clarity to make the feedback actionable and valuable."
            )
        )

    
    def _create_resume_refiner_agent(self):
        return Agent(
            role="Resume Refiner",
            goal="Apply refined feedback to enhance the resume, ensuring it highlights relevant skills and experiences.",
            tools=[],
            verbose=True,
            backstory=(
                "As a Resume Refiner, you specialize in enhancing resumes by integrating refined feedback, "
                "highlighting pertinent skills and experiences to align with job requirements and industry standards."
            )
        )
    
    def _create_cover_letter_refiner_agent(self):
        return Agent(
            role="Cover Letter Refiner",
            goal="Incorporate refined feedback into the cover letter to make it compelling and tailored to the job application.",
            tools=[],
            verbose=True,
            backstory=(
                "As a Cover Letter Refiner, you focus on embedding refined feedback into cover letters, "
                "crafting compelling narratives that are tailored to specific job applications and employer expectations."
            )
        )
    
    def _create_feedback_task(self):
        return Task(
            description=(
                "Generate comprehensive feedback based on the user's inputs {user_fb}, the "
                "feedback from NLP calculations on the originals the resume feedback {resumefb} and cover letter feedback {coverfb} , "
                "Focus on strengths, areas for improvement, and alignment with job requirements. "
                "Refine the generated feedback to enhance clarity and actionability."
            ),
            expected_output=(
                "An enhanced feedback report with clear, actionable items and refined language."
                "The feedback should provide valuable insights to improve the user's resume and cover letter."
            ),
            agent=self.feedback_compiling,
            dependencies=[],
            async_execution=False
        )
    
    
    def _create_resume_refinement_task(self):
        return Task(
            description=(
                "Refine the user's resume {resume} by integrating the feedback, emphasizing relevant skills and experiences."
            ),
            expected_output=(
                "An enhanced resume that effectively highlights the user's strengths and aligns with the job requirements."
            ),
            agent=self.resume_refiner,
            dependencies=[self.feedback_generation_task],
            async_execution=False
        )
    
    def _create_cover_letter_refinement_task(self):
        return Task(
            description=(
                "Refine the user's cover letter {cover} by incorporating the generated feedback, ensuring it is compelling and tailored to the job."
            ),
            expected_output=(
                "An optimized cover letter that is tailored to the job application, showcasing the user's qualifications and enthusiasm."
            ),
            agent=self.cover_letter_refiner,
            dependencies=[self.feedback_generation_task],
            async_execution=True
        )
