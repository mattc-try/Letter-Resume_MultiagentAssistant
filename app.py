from flask import Flask, render_template, request, jsonify
import logging
from agents.crewai_orchestrator import CrewaiOrchestrator

app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CrewAI Orchestrator
orchestrator = CrewaiOrchestrator()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs
        user_writeup = request.form['user_writeup']
        user_website = request.form['user_website']
        job_description = request.form['job_description']
        education = request.form['education']
        name = request.form['name']
        work_experience = request.form['work_experience']


        # Step 1: Perform Skill Matching
        logger.info("Performing skill matching...")
        try:
            skill_matching_results, sm_score = orchestrator.execute_skill_matching(
                job_posting_url=job_description,
                user_website=user_website,
                user_writeup=user_writeup
            )
        except Exception as e:
            logger.error(f"Error during skill matching: {e}")
            return render_template('index.html', skill_matching_results=f"Error: {e}")

        if not skill_matching_results:
            skill_matching_results = "Skill matching failed or returned no results."

        logger.info("Skill matching completed.")

        # # Step 2: Generate Resume and Cover Letter
        logger.info("Generating resume and cover letter...")
        cv = orchestrator.execute_resume_generation(skill_matching_results, name, work_experience, education)
        if not cv:
            return jsonify({"error": "Content generation failed."}), 500
        
        cover = orchestrator.execute_resume_generation(skill_matching_results, cv)
        if not cover:
            return jsonify({"error": "Content generation failed."}), 500

        # resume = content_generation_results.get('resume', 'Error generating resume.')
        # cover_letter = content_generation_results.get('cover_letter', 'Error generating cover letter.')
        # logger.info("Content generation completed.")

        # Step 3: Feedback and Refinement (Optional)
        # Placeholder for feedback and refinement logic

        # Render results
        return render_template(
            'index.html',
            resume=cv,
            cover_letter=cover,
            skill_matching_results=skill_matching_results,
            skill_matching_score=sm_score,
        )
    return render_template('index.html', skill_matching_results='', content_generation_results='')


if __name__ == '__main__':
    app.run(debug=True)
