from transformers import pipeline

class ContentGenerationAgent:
    def __init__(self):
        self.generator = pipeline('text-generation', model='gpt2')

    def generate_resume(self, user_profile, job_description):
        prompt = f"Create a professional resume based on the following user profile and job description.\n\nUser Profile:\n{user_profile}\n\nJob Description:\n{job_description}\n\nResume:"
        resume = self.generator(prompt, max_length=500, num_return_sequences=1)
        return resume[0]['generated_text']

    def generate_cover_letter(self, user_profile, job_description):
        prompt = f"Write a cover letter for the following user profile applying to this job.\n\nUser Profile:\n{user_profile}\n\nJob Description:\n{job_description}\n\nCover Letter:"
        cover_letter = self.generator(prompt, max_length=500, num_return_sequences=1)
        return cover_letter[0]['generated_text']
