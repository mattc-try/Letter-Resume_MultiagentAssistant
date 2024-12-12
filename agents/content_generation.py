# content_generation.py

import os
from crewai import Agent, Task, Crew
from transformers import pipeline
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
# from utils import get_openai_api_key, get_serper_api_key

class ContentGeneration:
    def __init__(self):
        
        # Initialize tools
        self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()
        
        # Initialize agents
        self.resume_strategist = self._create_resume_strategist()
        self.cover_letter_strategist = self._create_cover_letter_strategist()
        
    def _create_resume_strategist(self):
        return Agent(
            role="Resume Strategist",
            goal="Find all the best ways to make a resume stand out in the job market.",
            tools=[self.scrape_tool, self.search_tool],
            verbose=True,
            backstory=(
                "With a strategic mind and an eye for detail, you "
                "excel at creating resumes to highlight the most "
                "relevant skills and experiences, ensuring they "
                "resonate perfectly with the job's requirements."
            )
        )
    
    def _create_cover_letter_strategist(self):
        return Agent(
            role="Cover Letter Strategist",
            goal="Find all the best ways to make a cover letter stand out in the job market.",
            tools=[self.scrape_tool, self.search_tool],
            verbose=True,
            backstory=(
                "With a strategic mind and an eye for detail, you "
                "excel at creating cover letters to highlight the most "
                "relevant skills and experiences, ensuring they "
                "resonate perfectly with the job's requirements."
            )
        )
    
    def _create_resume_creation_task(self):
        return Task(
            description=(
                "Using the profile and job requirements obtained from "
                "previous tasks, create a resume for {name} with all necessary sections to highlight the most "
                "relevant areas. Employ tools to adjust and enhance the "
                "resume content. Make sure this is a resume of very good quality "
                "but don't make up any information. Write every section, "
                "including a summary, work experience with the {work_experience}, skills from {skill_matching_output}, "
                "and education {edu} sections. All to better reflect the candidate's "
                "abilities and how it matches the job posting."
            ),
            expected_output=(
                "A resume that effectively highlights the candidate's "
                "qualifications and experiences relevant to the job."
            ),
            # context=["skill_matching_output"],  # Assuming this refers to the output from SkillMatching crew
            agent=self.resume_strategist
        )
    
    def _create_cover_letter_creation_task(self):
        return Task(
            description=(
                "Using the profile and job requirements obtained from {skill_matching_output}"
                "and cv {generated_cv}, create a cover letter with all necessary information to highlight the most "
                "relevant areas. Employ tools to adjust and enhance the "
                "cover letter content. Make sure this is a cover letter of very good quality "
                "but don't make up any information. Write the content to better reflect the candidate's "
                "abilities and how it matches the job posting. "
                "Write an intriguing cover letter that boosts the chance of landing an interview."
            ),
            expected_output=(
                "A cover letter that effectively highlights the candidate's "
                "qualifications and experiences relevant to the job."
            ),
            # context=["skill_matching_output"],  # Assuming this refers to the output from SkillMatching crew
            agent=self.cover_letter_strategist
        )