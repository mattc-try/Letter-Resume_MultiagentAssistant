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


        # Step 1: Perform Skill Matching
        logger.info("Performing skill matching...")
        try:
            skill_matching_results = orchestrator.execute_skill_matching(
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
        content_generation_results = orchestrator.execute_content_generation(skill_matching_results)
        if not content_generation_results:
            return jsonify({"error": "Content generation failed."}), 500

        # resume = content_generation_results.get('resume', 'Error generating resume.')
        # cover_letter = content_generation_results.get('cover_letter', 'Error generating cover letter.')
        # logger.info("Content generation completed.")

        # Step 3: Feedback and Refinement (Optional)
        # Placeholder for feedback and refinement logic

        # Render results
        return render_template(
            'index.html',
            # resume=resume,
            # cover_letter=cover_letter,
            skill_matching_results=skill_matching_results,
            content_generation_results=content_generation_results
        )
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
