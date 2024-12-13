from flask import Flask, render_template, request, jsonify, send_file
import logging
from agents.crewai_orchestrator import CrewaiOrchestrator
import pdfkit
import os


app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CrewAI Orchestrator
orchestrator = CrewaiOrchestrator()

# Initialise websites for
resume_tips_website = 'https://www.businessnewsdaily.com/3207-resume-writing-tips.html'
coverLetter_tips_website = 'https://hbr.org/2022/05/how-to-write-a-cover-letter-that-sounds-like-you-and-gets-noticed'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs
        user_writeup = request.form['user_writeup']
        user_website = request.form['user_website']
        job_description = request.form['job_description']
        education = request.form['education']
        name = request.form['name']
        experience = request.form['experience']


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
        cv = orchestrator.execute_resume_generation(skill_matching_results, name, experience, education, resume_tips_website)
        if not cv:
            return jsonify({"error": "Content generation failed."}), 500
        
        cover = orchestrator.execute_cover_letter_generation(skill_matching_results, cv, coverLetter_tips_website)
        if not cover:
            return jsonify({"error": "Content generation failed."}), 500

        # resume = content_generation_results.get('resume', 'Error generating resume.')
        # cover_letter = content_generation_results.get('cover_letter', 'Error generating cover letter.')
        # logger.info("Content generation completed.")

        # Step 3: Feedback and Refinement (Optional)
        # Placeholder for feedback and refinement logic

        print("\n\n\nSkill Matching Results:", skill_matching_results)
        print("\n\n\nResume:", cv)
        print("\n\n\nCover Letter:", cover)
        print("\n\n\nSkill Matching Score:", sm_score)

        # Render results
        return render_template(
            'index.html',
            resume=cv,
            cover_letter=cover,
            skill_matching_results=skill_matching_results,
            skill_matching_score=sm_score,
        )
    return render_template('index.html', skill_matching_results='', content_generation_results='')


# Route for generating PDF
@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    resume = request.form.get('resume')
    cover_letter = request.form.get('cover_letter')

    # Generate HTML content to pass to pdfkit
    html_content = render_template('pdf_template.html', resume=resume, cover_letter=cover_letter)

    # Generate PDF from HTML using pdfkit
    pdf = pdfkit.from_string(html_content, False)

    # Save the PDF to a temporary file
    pdf_path = "static/generated_resume_coverletter.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf)

    # Return the generated PDF file to the user
    return send_file(pdf_path, as_attachment=True, download_name="Resume_and_Cover_Letter.pdf")


if __name__ == '__main__':
    app.run(debug=True)
