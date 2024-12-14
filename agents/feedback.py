from textblob import TextBlob
import textstat
import spacy
from transformers import pipeline

class Feedback:
    def __init__(self):
        # Initialize transformer-based grammar correction pipeline
        self.grammar_corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1")
        
        # Load spaCy model for NLP tasks
        self.nlp = spacy.load('en_core_web_sm')

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

        # 3. Sentiment Analysis using TextBlob
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        feedback['sentiment'] = {
            'polarity': polarity,
            'subjectivity': subjectivity
        }

        # 4. Structural Analysis
        structure_feedback = self.analyze_structure(content, content_type)
        feedback['structure'] = structure_feedback

        # 5. Tone Assessment
        tone_feedback = self.assess_tone(content)
        feedback['tone'] = tone_feedback

        # 6. Scoring and Score Explanation
        score, score_comment = self.calculate_score(feedback)
        feedback['score'] = score
        feedback['score_comment'] = score_comment

        # 7. Recommendations
        recommendations = self.generate_recommendations(feedback, content_type)
        feedback['recommendations'] = recommendations

        return feedback

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
        
        if polarity > 0.1:
            tone = 'Positive'
        elif polarity < -0.1:
            tone = 'Negative'
        else:
            tone = 'Neutral'

        return {
            'polarity': polarity,
            'tone': tone
        }

    def calculate_score(self, feedback):
        """
        A simple scoring mechanism combining grammar quality, readability, and sentiment.
        Scores will be between 0 and 100. Also provides a reason for the score.
        """
        # Start with a base score
        score = 100.0
        reasons = []

        # Deduct points based on grammar errors
        grammar_errors = feedback['grammar']['error_count']
        if grammar_errors > 0:
            score -= grammar_errors * 2
            reasons.append(f"{grammar_errors} grammar/spelling error(s) reduced the score.")

        # Adjust score based on readability (flesch_kincaid_grade as a proxy)
        fk_grade = feedback['readability']['flesch_kincaid_grade']
        if fk_grade > 12:
            diff = (fk_grade - 12) * 1.5
            score -= diff
            reasons.append(f"High reading level (Flesch-Kincaid {fk_grade:.2f}) reduced the score by {diff:.2f} points.")

        # Adjust based on sentiment polarity (encourage slightly positive/neutral)
        polarity = feedback['sentiment']['polarity']
        if polarity < -0.1:
            score -= 10
            reasons.append("Negative tone reduced the score by 10 points.")

        # Bound the score between 0 and 100
        score = max(0, min(100, score))

        if not reasons:
            reasons.append("No major issues; score remained high.")

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
        if feedback['tone']['tone'] == 'Negative':
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

# Example usage:
if __name__ == "__main__":
    # Sample resume content
    resume_content = """
    Salima Lamsiyah
    [Contact Information]

    Summary:
    Experienced Postdoctoral Researcher with a Ph.D. in Computer Science and AI, specializing in NLP and Generative AI models.
    Skilled in communication and research.

    Education:
    Ph.D. in Computer Science and AI

    Skills:
    - Artificial Intelligence
    - Natural Language Processing
    - Generative AI Models
    """

    # Sample cover letter content
    cover_letter_content = """
    Dear Hiring Manager,

    I am writing to express my interest in the Generative AI Engineer position.
    My experience with NLP and large language models demonstrates my ability
    to contribute effectively. Thank you for your consideration.

    Sincerely,
    Candidate Name
    """

    agent = Feedback()

    # Evaluate resume
    resume_feedback = agent.evaluate_content(resume_content, content_type="resume")
    print("Resume Feedback:")
    print(resume_feedback)

    # Evaluate cover letter
    cover_letter_feedback = agent.evaluate_content(cover_letter_content, content_type="cover_letter")
    print("\nCover Letter Feedback:")
    print(cover_letter_feedback)
