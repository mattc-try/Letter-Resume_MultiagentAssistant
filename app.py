# app.py

from flask import Flask, render_template, request
from agents.content_generation_agent import ContentGenerationAgent
from agents.skill_matching_agent import SkillMatchingAgent
from agents.feedback_refinement_agent import FeedbackRefinementAgent

app = Flask(__name__)

content_agent = ContentGenerationAgent()
skill_agent = SkillMatchingAgent()
feedback_agent = FeedbackRefinementAgent()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_profile = request.form['user_profile']
        job_description = request.form['job_description']

        # Generate Resume and Cover Letter
        resume = content_agent.generate_resume(user_profile, job_description)
        cover_letter = content_agent.generate_cover_letter(user_profile, job_description)

        # Skill Matching
        user_skills = skill_agent.extract_skills(user_profile)
        job_skills = skill_agent.extract_skills(job_description)
        matched_skills, missing_skills = skill_agent.match_skills(user_skills, job_skills)

        # Feedback and Refinement
        resume_feedback = feedback_agent.evaluate_content(resume)
        cover_letter_feedback = feedback_agent.evaluate_content(cover_letter)

        return render_template('index.html', resume=resume, cover_letter=cover_letter,
                               resume_feedback=resume_feedback, cover_letter_feedback=cover_letter_feedback,
                               matched_skills=matched_skills, missing_skills=missing_skills)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
