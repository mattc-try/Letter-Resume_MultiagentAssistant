import spacy

class SkillMatchingAgent:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def extract_skills(self, text):
        doc = self.nlp(text)
        skills = [ent.text for ent in doc.ents if ent.label_ == 'SKILL']
        return skills

    def match_skills(self, user_skills, job_skills):
        matched_skills = set(user_skills).intersection(set(job_skills))
        missing_skills = set(job_skills) - set(user_skills)
        return matched_skills, missing_skills
