from transformers import pipeline
from crewai import Agent, Task, Crew
import os
from utils import get_openai_api_key, get_serper_api_key
from crewai_tools import (
  ScrapeWebsiteTool,
  SerperDevTool
)

# OpenAI: sk-RkFZVILgHMDgIz7GcMMRu-05S0qnAHD5kgBSdxxdMJT3BlbkFJ2TpIkjqkdqeSQf0fWB8EYdX_wyuMZuSQnMJ0UaeRsA
# Serper: 1a8aaaa7f0219ee9e9d82d0f4c1fbc650fccf5d3

openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
os.environ["SERPER_API_KEY"] = get_serper_api_key()

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Agent Resume Strategist
resume_strategist = Agent(
    role="Resume Strategist",
    goal="Find all the best ways to make a "
         "resume stand out in the job market.",
    tools = [scrape_tool, search_tool],
    verbose=True,
    backstory=(
        "With a strategic mind and an eye for detail, you "
        "excel at creating resumes to highlight the most "
        "relevant skills and experiences, ensuring they "
        "resonate perfectly with the job's requirements."
    )
)

# Agent Cover Letter Strategist
coverLetter_strategist = Agent(
    role="Cover Letter Strategist",
    goal="Find all the best ways to make a "
         "cover letter stand out in the job market.",
    tools = [scrape_tool, search_tool],
    verbose=True,
    backstory=(
        "With a strategic mind and an eye for detail, you "
        "excel at creating cover letters to highlight the most "
        "relevant skills and experiences, ensuring they "
        "resonate perfectly with the job's requirements."
    )
)

# Task for Resume Strategist Agent: Create a Resume aligned with Job Requirements
resume_creation_task = Task(
    description=(
        "Using the profile and job requirements obtained from "
        "previous tasks, create a resume with all necessary sections to highlight the most "
        "relevant areas. Employ tools to adjust and enhance the "
        "resume content. Make sure this is a resume of very good quality "
        "but don't make up any information. Write every section, "
        "inlcuding a summary, work experience, skills, "
        "and education sections. All to better reflrect the candidates "
        "abilities and how it matches the job posting."
    ),
    expected_output=(
        "A resume that effectively highlights the candidate's "
        "qualifications and experiences relevant to the job."
    ),
    context=[research_task, profile_task], # to make use of the output of skill matching agents
    agent=resume_strategist
)

# Task for Cover Letter Strategist Agent: Create a Resume aligned with Job Requirements
coverLetter_creation_task = Task(
    description=(
        "Using the profile and job requirements obtained from "
        "previous tasks, create a cover letter with all necessary information to highlight the most "
        "relevant areas. Employ tools to adjust and enhance the "
        "cover letter content. Make sure this is a cover letter of very good quality "
        "but don't make up any information. Write the content to better reflrect the candidates "
        "abilities and how it matches the job posting. "
        "Write an intriguing cover letter that boosts the chance of landing an interview."
    ),
    expected_output=(
        "A cover letter that effectively highlights the candidate's "
        "qualifications and experiences relevant to the job."
    ),
    context=[research_task, profile_task], # to make use of the output of skill matching agents
    agent=resume_strategist
)

content_generation_crew = Crew(
    agents=[resume_strategist,
            coverLetter_strategist],

    tasks=[resume_creation_task,
           coverLetter_creation_task],
    verbose=True
)

# class ContentGenerationAgent:
#     def __init__(self):
#         self.generator = pipeline('text-generation', model='gpt2')
# 
#     def generate_resume(self, user_profile, job_description):
#         prompt = f"Create a professional resume based on the following user profile and job description.\n\nUser Profile:\n{user_profile}\n\nJob Description:\n{job_description}\n\nResume:"
#         resume = self.generator(prompt, max_length=500, num_return_sequences=1)
#         return resume[0]['generated_text']
# 
#     def generate_cover_letter(self, user_profile, job_description):
#         prompt = f"Write a cover letter for the following user profile applying to this job.\n\nUser Profile:\n{user_profile}\n\nJob Description:\n{job_description}\n\nCover Letter:"
#         cover_letter = self.generator(prompt, max_length=500, num_return_sequences=1)
#         return cover_letter[0]['generated_text'] 