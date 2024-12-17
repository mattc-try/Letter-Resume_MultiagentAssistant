# MIT License
# 
# Copyright (c) 2024 mattc-try (GitHub)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
from flask import Flask, render_template, request, jsonify, send_file
import logging
from agents.crewai_orchestrator import CrewaiOrchestrator
import pdfkit
import os

# Initialize the Flask application
app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CrewAI Orchestrator (Custom Orchestrator class handling the logic)
orchestrator = CrewaiOrchestrator()

# URLs for content generation tips
resume_tips_website = 'https://www.businessnewsdaily.com/3207-resume-writing-tips.html'
coverLetter_tips_website = 'https://hbr.org/2022/05/how-to-write-a-cover-letter-that-sounds-like-you-and-gets-noticed'


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Route: / (root)
    Methods: GET, POST
    
    - On GET: Renders the homepage form for content inputs.
    - On POST: Processes user inputs to perform the following tasks:
        1. Skill Matching: Matches user input against job description.
        2. Content Generation: Generates a resume and cover letter.
        3. Feedback Score: Calculates feedback scores for the generated content.
    
    Returns:
        - HTML template populated with skill matching results, generated resume, and cover letter.
    """
    if request.method == 'POST':
        # Extract user inputs from the form
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
                user_writeup=user_writeup,
                edu=education,
                work_experience=experience
            )
        except Exception as e:
            logger.error(f"Error during skill matching: {e}")
            return render_template('index.html', skill_matching_results=f"Error: {e}")

        if not skill_matching_results:
            skill_matching_results = "Skill matching failed or returned no results."

        logger.info("Skill matching completed.")
        
        # Step 2: Generate Resume and Cover Letter
        logger.info("Generating resume and cover letter...")
        cv, cover = orchestrator.execute_content_generation(skill_matching_results, name, experience, education, resume_tips_website, coverLetter_tips_website)
        if not cv or not cover:
            return jsonify({"error": "Content generation failed."}), 500

        # Step 3: Calculate Feedback Score
        _, rsc = orchestrator.calculate_feedback_score(cv, content_type="resume")
        _, csc = orchestrator.calculate_feedback_score(cover, content_type="cover_letter")

        # Render the results back to the template
        return render_template(
            'index.html',
            resume=cv,
            cover_letter=cover,
            skill_matching_results=skill_matching_results,
            skill_matching_score=sm_score,
            askuserfb=True,
            show_form=False,
            rsc=rsc,
            csc=csc
        )
    
    # On GET request, show an empty form
    return render_template('index.html', skill_matching_results='', content_generation_results='', show_form=True)


@app.route('/refine', methods=['POST', 'GET'])
def refine():
    """
    Route: /refine
    Methods: POST, GET
    
    - Refines the generated resume and cover letter based on user feedback.
    
    Inputs:
        - User feedback
        - Previously generated resume and cover letter
    
    Returns:
        - Updated HTML template with refined resume and cover letter.
    """
    # Extract feedback and existing content
    user_feedback = request.form['userfb']
    resume = request.form['resume']
    cover_letter = request.form['cover_letter']

    logger.info("Refining content based on user feedback...")
    # Refine the content using the orchestrator
    fb, refined_resume, refined_cover, rsc, csc = orchestrator.execute_feedback_refinement(resume, cover_letter, user_feedback)
    if not fb or not refined_resume or not refined_cover:
        return jsonify({"error": "Refinement failed."}), 500

    return render_template(
        'index.html',
        resume=refined_resume,
        cover_letter=refined_cover,
        askuserfb=True,
        fb=fb,
        rsc=rsc,
        csc=csc
    )


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """
    Route: /download-pdf
    Methods: POST
    
    - Generates a PDF containing the resume and cover letter provided in the form.
    
    Inputs:
        - Resume and cover letter text
    
    Returns:
        - A downloadable PDF file.
    """
    # Extract resume and cover letter content from form
    resume = request.form.get('resume')
    cover_letter = request.form.get('cover_letter')

    # Generate HTML content for PDF generation
    html_content = render_template('pdf_template.html', resume=resume, cover_letter=cover_letter)

    # Convert the HTML content to PDF using pdfkit
    pdf = pdfkit.from_string(html_content, False)

    # Save PDF to a temporary file
    pdf_path = "static/generated_resume_coverletter.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf)

    # Send the generated PDF file to the user as a download
    return send_file(pdf_path, as_attachment=True, download_name="Resume_and_Cover_Letter.pdf")


if __name__ == '__main__':
    """
    Runs the Flask development server.
    """
    app.run(debug=True)
