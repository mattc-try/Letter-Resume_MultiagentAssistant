# app.py

from flask import Flask, render_template, request
import json
import logging

from crewai.crewai_orchestrator import main as crewai_main
from crewai import Orchestrator  # Assuming CrewAI provides an Orchestrator class

app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CrewAI Orchestrator in a separate thread or process
import threading

def start_crewai():
    crewai_main()

crewai_thread = threading.Thread(target=start_crewai, daemon=True)
crewai_thread.start()
logger.info("CrewAI Orchestrator started in a separate thread.")

# Initialize a client to communicate with CrewAI
from crewai import Client  # Assuming CrewAI provides a Client class

crewai_client = Client(
    communication_protocol='json',
    task_queue='redis://localhost:6379/0'
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_profile = request.form['user_profile']
        job_description = request.form['job_description']

        # Step 1: Generate Resume
        resume_response = crewai_client.send_task(
            agent='ContentGenerationAgent',
            task='generate_resume',
            payload={
                'user_profile': user_profile,
                'job_description': job_description
            }
        )
        resume = resume_response.get('resume', 'Error generating resume.')

        # Step 2: Generate Cover Letter
        cover_letter_response = crewai_client.send_task(
            agent='ContentGenerationAgent',
            task='generate_cover_letter',
            payload={
                'user_profile': user_profile,
                'job_description': job_description
            }
        )
        cover_letter = cover_letter_response.get('cover_letter', 'Error generating cover letter.')

        # Step 3: Skill Matching
        user_skills = extract_skills(user_profile)
        job_skills = extract_skills(job_description)
        skill_matching_response = crewai_client.send_task(
            agent='SkillMatchingAgent',
            task='match_skills',
            payload={
                'user_skills': user_skills,
                'job_skills': job_skills
            }
        )
        matched_skills = skill_matching_response.get('matched_skills', [])
        missing_skills = skill_matching_response.get('missing_skills', [])

        # Step 4: Feedback and Refinement for Resume
        resume_feedback_response = crewai_client.send_task(
            agent='FeedbackRefinementAgent',
            task='evaluate_content',
            payload={
                'content': resume,
                'job_description': job_description
            }
        )
        resume_feedback = resume_feedback_response

        # Step 5: Feedback and Refinement for Cover Letter
        cover_letter_feedback_response = crewai_client.send_task(
            agent='FeedbackRefinementAgent',
            task='evaluate_content',
            payload={
                'content': cover_letter,
                'job_description': job_description
            }
        )
        cover_letter_feedback = cover_letter_feedback_response

        return render_template('index.html', resume=resume, cover_letter=cover_letter,
                               resume_feedback=resume_feedback, cover_letter_feedback=cover_letter_feedback,
                               matched_skills=matched_skills, missing_skills=missing_skills)
    return render_template('index.html')

def extract_skills(text):
    # Placeholder for skill extraction logic
    # You can implement skill extraction using spaCy or other NLP techniques
    import spacy
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    skills = [ent.text for ent in doc.ents if ent.label_ == 'SKILL']  # Assuming 'SKILL' label exists
    return skills

if __name__ == '__main__':
    app.run(debug=True)
