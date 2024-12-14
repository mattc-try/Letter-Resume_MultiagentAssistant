# content_generation.py

import os
from crewai import Agent, Task, Crew
from transformers import pipeline
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
# from utils import get_openai_api_key, get_serper_api_key

class ContentGeneration:
    def __init__(self):
        
        # Initialize tools
        # self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()
        
        # Initialize agents
        self.resume_strategist = self._create_resume_strategist()
        self.cover_letter_strategist = self._create_cover_letter_strategist()
        self.resume_formatter = self._create_resume_formatter()
        
    def _create_resume_strategist(self):
        return Agent(
            role="Resume Strategist",
            goal="Find all the best ways to make a resume stand out in the job market.",
            # tools=[self.scrape_tool, self.search_tool],
            tools=[self.scrape_tool],
            verbose=True,
            backstory=(
                "With a strategic mind and an eye for detail, you "
                "excel at creating clear and comphrehensive resumes to highlight the most "
                "relevant skills and experiences, ensuring they "
                "resonate perfectly with the job's requirements."
            )
        )
    
    def _create_cover_letter_strategist(self):
        return Agent(
            role="Cover Letter Strategist",
            goal="Find all the best ways to make a cover letter stand out in the job market.",
            # tools=[self.scrape_tool, self.search_tool],
            tools=[self.scrape_tool],
            verbose=True,
            backstory=(
                "With a strategic mind and an eye for detail, you "
                "excel at creating cover letters to highlight the most "
                "relevant skills and experiences, ensuring they "
                "resonate perfectly with the job's requirements."
            )
        )
    
    def _create_resume_formatter(self):
        return Agent(
            role="Resume Formatter",
            goal=(
                "Format the resume information into a professional and clear structure based "
                "on predefined formatting instructions."
            ),
            verbose=True,
            backstory=(
                "A formatting expert with a keen eye for professional and clear design, you "
                "ensure that resumes adhere to industry standards and enhance their "
                "presentation to make the best impression and make them easy to read."
            )
        )
    
    def _create_resume_creation_task(self):
        return Task(
            description=(
                "Using the profile and job requirements obtained from "
                "previous tasks, create a resume for {name} with all necessary sections to highlight the most "
                "relevant areas. Employ tools to adjust and enhance the "
                "resume content and apply the tips from {resume_tips_website}. "
                "Make sure this is a resume of very good quality and clear structure, "
                "but don't make up any information. Write every section, "
                "including an Introduction section, education section with {edu}, work experience section with the {work_experience}, skills section from {skill_matching_output}. "
                "All to better reflect the candidate's abilities and how it matches the job posting. "
                "Also add a section about Language skills if you have this information about {name}. "
                "Only add candidate's skills that match the job ones, and no suggestion for improvement."
            ),
            expected_output=(
                "A clear and comphrehensive resume that effectively highlights the candidate's "
                "qualifications and experiences relevant to the job."
            ),
            agent=self.resume_strategist,
            async_execution=False
        )
    
    def _create_cover_letter_creation_task(self):
        return Task(
            description=(
                "Using the profile and job requirements obtained from {skill_matching_output}"
                "and resume, create a cover letter with all necessary information to highlight the most "
                "relevant areas. Employ tools to adjust and enhance the "
                "cover letter content and apply the tips from {coverLetter_tips_website}. Make sure this is a cover letter of very good quality "
                "but don't make up any information. Write the content to better reflect the candidate's "
                "abilities and how it matches the job posting. Make it clear and professional, to boost the chance of landing an interview."
            ),
            expected_output=(
                "A cover letter that effectively highlights the candidate's "
                "qualifications and experiences relevant to the job."
            ),
            agent=self.cover_letter_strategist,
            async_execution=False
        )
    
    def _create_resume_formatting_task(self):
        return Task(
            description=(
                "Format the resume content provided by the Resume Strategist agent into a professional template. "
                "Ensure the resume includes the following sections in order: Introduction, Education, Work Experience, Skills, Language Skills. "
                "Section titles should be in bold, and the layout should be clean and easy to read, use bullet points. "
                "Ensure proper indentation, alignment, and spacing to make the resume visually appealing. "
                "Don't fill in the sections with fake information. All information should be taken from the resume information provided by the Resume Strategist agent. "
                "If you don't have the necessary information for one of the sections, don't add it to the final output. "
            ),
            expected_output=(
                "A professionally formatted resume that adheres to the predefined formatting guidelines."
            ),
            agent=self.resume_formatter,
            dependencies=[self._create_resume_creation_task],
            async_execution=False
        )