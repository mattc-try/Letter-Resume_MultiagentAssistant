# agents/feedback_refinement_agent.py

from textblob import TextBlob

class FeedbackRefinementAgent:
    def __init__(self):
        pass

    def evaluate_content(self, content):
        feedback = {}
        # Grammar and Spelling Check
        blob = TextBlob(content)
        corrected_content = str(blob.correct())
        feedback['grammar'] = corrected_content

        # Readability Score (Flesch-Kincaid)
        words = len(blob.words)
        sentences = len(blob.sentences)
        syllables = sum([blob.word_counts[word] for word in blob.words])
        readability = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        feedback['readability'] = readability

        # Suggestions
        feedback['suggestions'] = "Consider simplifying complex sentences." if readability < 60 else "Content is clear and easy to read."

        return feedback
