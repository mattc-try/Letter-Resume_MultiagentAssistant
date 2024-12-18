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


import os
import warnings
import requests
from crewai import Agent, Task, Crew
from transformers import pipeline
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from agents.skill_matching import SkillMatching
from agents.content_generation import ContentGeneration
from agents.feedback_refinement import FeedbackRefinement


class CrewaiOrchestrator:
    def __init__(self):
        # Suppress warnings
        warnings.filterwarnings('ignore')

        # Initialize API keys and environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "fallback-openai-api-key")
        os.environ["OPENAI_MODEL_NAME"] = 'gpt-4-turbo'
        os.environ["SERPER_API_KEY"] = self.get_serper_api_key()

        # Initialize tools
        # self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()

        # Initialize SkillMatching instance
        skill_matching = SkillMatching()  # Create an instance of SkillMatching

        # Initialize Agents for Skill Matching
        self.researcher = skill_matching._create_researcher_agent()
        self.profiler = skill_matching._create_profiler_agent()
        self.skill_matcher = skill_matching._create_skill_matcher_agent()

        # Initialize Tasks for Skill Matching
        self.research_task = skill_matching._create_research_task()
        self.profile_task = skill_matching._create_profile_task()
        self.skill_matching_task = skill_matching._create_skill_matching_task()

        # Initialize ContentGeneration instance
        content_generation = ContentGeneration()  # Create an instance of ContentGeneration

        # Initialize Agents for Content Generation
        self.resume_strategist = content_generation._create_resume_strategist()
        self.cover_letter_strategist = content_generation._create_cover_letter_strategist()
        self.resume_formatter = content_generation._create_resume_formatter()

        # Initialize Tasks for Content Generation
        self.resume_creation_task = content_generation._create_resume_creation_task()
        self.cover_letter_creation_task = content_generation._create_cover_letter_creation_task()
        self.resume_formatting_task = content_generation._create_resume_formatting_task()


        # Define Flask API endpoint
        self.flask_api_endpoint = 'http://localhost:5000/api'  # Update as needed


    def execute_skill_matching(self, job_posting_url, user_website, user_writeup, edu, work_experience):
        """
        Executes the skill matching crew with the provided inputs.

        Args:
            job_posting_url (str): URL of the job posting.
            linkedin_profile_url (str): URL of the user's LinkedIn profile.

        Returns:
            dict: Skill matching results.
        """
        classs = SkillMatching()
        # Initialize Crew for Skill Matching
        self.skill_matching_crew = Crew(
            agents=[
                self.researcher,
                self.profiler,
                self.skill_matcher
            ],
            tasks=[
                self.research_task,
                self.profile_task,
                self.skill_matching_task
            ],
            verbose=True
        )

        inputs = {
            'job_posting_url': job_posting_url,
            'user_website': user_website,
            'user_writeup': user_writeup,
            'edu': edu,
            'work_experience': work_experience
        }
        result = self.skill_matching_crew.kickoff(inputs=inputs)
        score = classs.compute_score(result.raw)
        return result, score 
    
    def execute_content_generation(self, skill_matching_output, name, work_experience, edu, resume_tips_website, coverLetter_tips_website):
        """
        Executes the content generation crew using skill matching results.

        Args:
            skill_matching_output (dict): Output from the skill matching process.

        Returns:
            dict: Content generation results.
        """

        # Initialize Crew for Content Generation
        self.content_generation_crew = Crew(
            agents=[
                self.resume_strategist,
                self.cover_letter_strategist,
                self.resume_formatter
            ],
            tasks=[
                self.resume_creation_task,
                self.cover_letter_creation_task,
                self.resume_formatting_task
            ],
            verbose=True,
            full_output=True
        )

        inputs = {
            'skill_matching_output': skill_matching_output,
            'name': name,
            'work_experience': work_experience,
            'edu': edu,
            'resume_tips_website': resume_tips_website,
            'coverLetter_tips_website': coverLetter_tips_website,
        }
        result = self.content_generation_crew.kickoff(inputs=inputs)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        # for task in result.tasks_output:
        #     # print(task.task_id)
        #     print(task)
        cv = result.tasks_output[0]
        cover = result.tasks_output[1]
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        
        return cv, cover
    

    def execute_feedback_refinement(self, resume, cover, user_fb):
        """
        Gives feedback to the user based on the generated content.

        Args:
            feedback (str): User feedback on the generated content.

        Returns:
            str: Feedback response.
        """
        fb = FeedbackRefinement()

        resumefb, rsc = fb.evaluate_content(resume, content_type="resume")
        print(resumefb)
        coverfb, csc = fb.evaluate_content(cover, content_type="cover_letter")
        print(coverfb)

        # Initialize Crew for Feedback
        self.feedback_crew = Crew(
            agents=[
                fb._create_feedback_compiling_agent(),
                fb._create_feedback_refinement_agent(),
                fb._create_resume_refiner_agent(),
                fb._create_cover_letter_refiner_agent()
            ],
            tasks=[
                fb._create_feedback_task(),
                fb._create_resume_refinement_task(),
                fb._create_cover_letter_refinement_task()
            ],
            verbose=True,
            full_output=True
        )

        inputs = {
            'user_fb': user_fb,
            'resumefb': resumefb,
            'coverfb': coverfb,
            'resume': resume,
            'cover': cover,
        }
        result = self.feedback_crew.kickoff(inputs=inputs)
        feed = result.tasks_output[0]
        resume_refined = result.tasks_output[1]
        cover_refined = result.tasks_output[2]


        _, rsc = fb.evaluate_content(resume_refined.raw, content_type="resume")
        _, csc = fb.evaluate_content(cover_refined.raw, content_type="cover_letter")

        return feed, resume_refined, cover_refined, rsc, csc
    
    def calculate_feedback_score(self, content, content_type):
        """
        Calculates the feedback score based on the user feedback and the generated content.

        Args:
            content (str): Generated content.
            user_feedback (str): User feedback on the content.

        Returns:
            float: Feedback score.
        """
        score = 0.0
        fb = FeedbackRefinement()

        fb, score = fb.evaluate_content(content.raw, content_type)

        return fb, score

    




    

    def send_to_flask(self, data, endpoint):
        """
        Sends data to the specified Flask endpoint via HTTP POST.

        Args:
            data (dict): Data payload to send.
            endpoint (str): Specific Flask API endpoint.

        Returns:
            bool: True if successful, False otherwise.
        """
        url = f"{self.flask_api_endpoint}/{endpoint}"
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print(f"Successfully sent data to Flask endpoint: {endpoint}")
                return True
            else:
                print(f"Failed to send data to Flask endpoint: {endpoint}. Status Code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending data to Flask endpoint: {endpoint}. Error: {e}")
            return False

    def orchestrate(self, job_posting_url, linkedin_profile_url):
        """
        Orchestrates the entire process: skill matching, content generation, and sending results to Flask.

        Args:
            job_posting_url (str): URL of the job posting.
            linkedin_profile_url (str): URL of the user's LinkedIn profile.

        Returns:
            dict: Final results from content generation.
        """
        # Step 1: Skill Matching
        print("Starting Skill Matching...")
        skill_matching_results = self.execute_skill_matching(job_posting_url, linkedin_profile_url)
        print("Skill Matching Completed.")

        # Step 2: Send Skill Matching Results to Flask
        skill_matching_payload = {
            'job_requirements': skill_matching_results.get('job_requirements'),
            'user_profile': skill_matching_results.get('user_profile'),
            'skill_matching_output': skill_matching_results.get('skill_matching_output')
        }
        self.send_to_flask(skill_matching_payload, 'skill-matching-result')

        # Step 3: Content Generation
        print("Starting Content Generation...")
        content_generation_results = self.execute_content_generation(skill_matching_results)
        print("Content Generation Completed.")

        # Step 4: Send Content Generation Results to Flask
        content_payload = {
            'resume': content_generation_results.get('resume'),
            'cover_letter': content_generation_results.get('cover_letter')
        }
        self.send_to_flask(content_payload, 'content-generation-result')

        return content_generation_results
    
    def get_serper_api_key(self):
        return os.getenv('1a8aaaa7f0219ee9e9d82d0f4c1fbc650fccf5d3', 'fallback-serper-api-key')
