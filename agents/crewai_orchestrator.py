# crewai_orchestrator.py

import os
import warnings
import requests
from crewai import Agent, Task, Crew
from transformers import pipeline
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from agents.skill_matching import SkillMatching
from agents.content_generation import ContentGeneration


class CrewaiOrchestrator:
    def __init__(self):
        # Suppress warnings
        warnings.filterwarnings('ignore')

        # Initialize API keys and environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "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")
        os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
        os.environ["SERPER_API_KEY"] = self.get_serper_api_key()

        # Initialize tools
        self.search_tool = SerperDevTool()
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

        # Initialize Tasks for Content Generation
        self.resume_creation_task = content_generation._create_resume_creation_task()
        self.cover_letter_creation_task = content_generation._create_cover_letter_creation_task()


        # Define Flask API endpoint
        self.flask_api_endpoint = 'http://localhost:5000/api'  # Update as needed


    def execute_skill_matching(self, job_posting_url, user_website, user_writeup):
        """
        Executes the skill matching crew with the provided inputs.

        Args:
            job_posting_url (str): URL of the job posting.
            linkedin_profile_url (str): URL of the user's LinkedIn profile.

        Returns:
            dict: Skill matching results.
        """
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
            'user_writeup': user_writeup
        }
        result = self.skill_matching_crew.kickoff(inputs=inputs)
        score = self.skill_matching.compute_score()
        return result, score 
    
    def execute_cover_leter_generation(self, skill_matching_output, generated_cv):
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
                self.cover_letter_strategist
            ],
            tasks=[
                self.cover_letter_creation_task
            ],
            verbose=True
        )

        inputs = {
            'skill_matching_output': skill_matching_output,
            'generated_cv': generated_cv
        }
        result = self.content_generation_crew.kickoff(inputs=inputs)
        return result
    
    def execute_resume_generation(self, skill_matching_output, name, work_experience, edu):
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
            ],
            tasks=[
                self.resume_creation_task,
            ],
            verbose=True
        )

        inputs = {
            'skill_matching_output': skill_matching_output,
            'name': name,
            'work_experience': work_experience,
            'edu': edu
        }
        result = self.content_generation_crew.kickoff(inputs=inputs)
        return result
    
    

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
    
    def get_openai_api_key(self):
        return os.getenv('sk-RkFZVILgHMDgIz7GcMMRu-05S0qnAHD5kgBSdxxdMJT3BlbkFJ2TpIkjqkdqeSQf0fWB8EYdX_wyuMZuSQnMJ0UaeRsA', 'fallback-openai-api-key')

    def get_serper_api_key(self):
        return os.getenv('1a8aaaa7f0219ee9e9d82d0f4c1fbc650fccf5d3', 'fallback-serper-api-key')

# # Example usage (this should be called from your Flask routes or other parts of the app)
# if __name__ == "__main__":
#     orchestrator = CrewaiOrchestrator()
#     job_url = 'https://jobs.lever.co/AIFund/6c82e23e-d954-4dd8-a734-c0c2c5ee00f1?lever-origin=applied&lever-source%5B%5D=AI+Fund'
#     linkedin_url = 'https://www.linkedin.com/in/matteo-steinbach-724547284/'
#     final_results = orchestrator.orchestrate(job_url, linkedin_url)
#     print("Content Generation Results:", final_results)
