# agents/feedback_refinement_agent.py

from textblob import TextBlob
import textstat
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline

class FeedbackRefinementAgent:
    def __init__(self, job_description=""):
        # Initialize LanguageTool for grammar and style checking (optional if using transformer-based model)
        # self.tool = language_tool_python.LanguageTool('en-US')  # Optional: Can be removed if fully replacing
        
        # Initialize transformer-based grammar correction pipeline
        self.grammar_corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1")
        
        # Load spaCy model for NLP tasks
        self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.job_description = job_description
        self.job_vector = None
        if job_description:
            self.job_vector = self.vectorizer.fit_transform([job_description])

    def set_job_description(self, job_description):
        self.job_description = job_description
        self.job_vector = self.vectorizer.fit_transform([job_description])

    def evaluate_content(self, content):
        feedback = {}

        # 1. Grammar and Spell Checking using Transformer-based Model
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

        # 3. Clarity and Conciseness using TextBlob
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        feedback['sentiment'] = {
            'polarity': polarity,
            'subjectivity': subjectivity
        }

        # 4. Structural Analysis
        structure_feedback = self.analyze_structure(content)
        feedback['structure'] = structure_feedback

        # 5. Content Relevance
        relevance_feedback = self.analyze_relevance(content)
        feedback['relevance'] = relevance_feedback

        # 6. Tone Assessment
        tone_feedback = self.assess_tone(content)
        feedback['tone'] = tone_feedback

        # 7. Keyword Optimization
        keyword_feedback = self.optimize_keywords(content)
        feedback['keywords'] = keyword_feedback

        return feedback

    def correct_grammar(self, content):
        """
        Correct grammar and spelling using a transformer-based model.
        """
        corrected = self.grammar_corrector(content, max_length=512, truncation=True)
        corrected_text = corrected[0]['generated_text']
        
        # To identify the differences, you can compare the original and corrected texts.
        # For simplicity, we'll just return the corrected text.
        # For more detailed feedback, consider implementing a diffing mechanism.
        
        # Calculate the number of changes
        original_words = set(content.split())
        corrected_words = set(corrected_text.split())
        num_errors = len(original_words.symmetric_difference(corrected_words))
        
        # Example: Find specific changes (this is a simplistic approach)
        # For a more accurate error identification, consider using alignment algorithms.
        errors = []
        for original, corrected in zip(content.split(), corrected_text.split()):
            if original != corrected:
                errors.append(f"Original: {original} --> Corrected: {corrected}")
        
        return {
            'error_count': num_errors,
            'errors': errors,
            'corrected_content': corrected_text
        }

    def analyze_structure(self, content):
        # Define standard sections for a resume
        standard_sections = [
            'Contact Information',
            'Professional Summary',
            'Work Experience',
            'Education',
            'Skills',
            'Certifications',
            'Projects',
            'Volunteer Experience'
        ]

        doc = self.nlp(content)
        found_sections = set()

        for sent in doc.sents:
            for section in standard_sections:
                if section.lower() in sent.text.lower():
                    found_sections.add(section)

        missing_sections = set(standard_sections) - found_sections

        return {
            'found_sections': list(found_sections),
            'missing_sections': list(missing_sections)
        }

    def analyze_relevance(self, content):
        if not self.job_vector:
            return {
                'message': 'Job description not provided. Relevance analysis not available.'
            }

        # Compute TF-IDF vectors
        documents = [content, self.job_description]
        tfidf_matrix = self.vectorizer.transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        return {
            'similarity_score': similarity,
            'message': f"Content has a similarity score of {similarity:.2f} with the job description."
        }

    def assess_tone(self, content):
        # Simple sentiment analysis using TextBlob
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity  # Range: [-1.0, 1.0]
        subjectivity = blob.sentiment.subjectivity  # Range: [0.0, 1.0]

        if polarity > 0.1:
            tone = 'Positive'
        elif polarity < -0.1:
            tone = 'Negative'
        else:
            tone = 'Neutral'

        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'tone': tone
        }

    def optimize_keywords(self, content):
        if not self.job_vector:
            return {
                'message': 'Job description not provided. Keyword optimization not available.'
            }

        # Extract keywords from job description using TF-IDF
        job_keywords = self.extract_keywords(self.job_description)

        # Extract keywords from content
        content_keywords = self.extract_keywords(content)

        matched_keywords = set(job_keywords).intersection(set(content_keywords))
        missing_keywords = set(job_keywords) - set(content_keywords)

        return {
            'matched_keywords': list(matched_keywords),
            'missing_keywords': list(missing_keywords),
            'suggestions': f"Consider adding the following keywords to improve ATS compatibility: {', '.join(missing_keywords)}" if missing_keywords else "All relevant keywords are included."
        }

    def extract_keywords(self, text, num_keywords=10):
        doc = self.nlp(text.lower())
        keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform([' '.join(keywords)])
        feature_array = np.array(tfidf.get_feature_names_out())
        tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
        top_n = feature_array[tfidf_sorting][:num_keywords]
        return top_n.tolist()
