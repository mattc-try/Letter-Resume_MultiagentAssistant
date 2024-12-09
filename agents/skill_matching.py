# skill_matching.py

# Warning control
import warnings
warnings.filterwarnings('ignore')

from crewai import Agent, Task, Crew

import os
from utils import get_openai_api_key, get_serper_api_key

# Retrieve API keys
openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
os.environ["SERPER_API_KEY"] = get_serper_api_key()

from crewai_tools import (
    ScrapeWebsiteTool,
    SerperDevTool
)

from agents.skill_matching_agent import SkillMatchingAgent  # Import SkillMatcherAgent

# Initialize tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Agent 1: Researcher
researcher = Agent(
    role="Tech Job Researcher",
    goal="Make sure to do amazing analysis on job posting to help job applicants",
    tools=[scrape_tool, search_tool],
    verbose=True,
    backstory=(
        "As a Job Researcher, your prowess in navigating and extracting critical "
        "information from job postings is unmatched. "
        "Your skills help pinpoint the necessary qualifications and skills sought "
        "by employers, forming the foundation for effective application tailoring."
    )
)

# Agent 2: Profiler
profiler = Agent(
    role="Personal Profiler for Engineers",
    goal="Do incredible research on job applicants to help them stand out in the job market",
    tools=[scrape_tool, search_tool],
    verbose=True,
    backstory=(
        "Equipped with analytical prowess, you dissect and synthesize information "
        "from diverse sources to craft comprehensive personal and professional profiles, "
        "laying the groundwork for personalized resume enhancements."
    )
)

# Agent 3: Skill Matcher
skill_matcher = SkillMatchingAgent(
    agent_id="SkillMatcher",
    config={}
)

# Task for Researcher Agent: Extract Job Requirements
research_task = Task(
    description=(
        "Analyze the job posting URL provided ({job_posting_url}) "
        "to extract key skills, experiences, and qualifications "
        "required. Use the tools to gather content and identify "
        "and categorize the requirements."
    ),
    expected_output=(
        "A structured list of job requirements, including necessary "
        "skills, qualifications, and experiences."
    ),
    agent=researcher,
    async_execution=True
)

# Task for Profiler Agent: Compile Comprehensive Profile
profile_task = Task(
    description=(
        "Compile professional profile "
        "using the LinkedIn ({linkedin_profile_url}) URL to find the user's skills, education, and work experiences. "
        "Utilize tools to extract and "
        "synthesize information from these sources."
    ),
    expected_output=(
        "A comprehensive profile document that includes skills, "
        "project experiences, contributions, interests, and "
        "communication style."
    ),
    agent=profiler,
    async_execution=True
)

# Task for Skill Matcher Agent: Match Skills and Extract Relevant LinkedIn Information
skill_matching_task = Task(
    description=(
        "Using the job requirements and the user's comprehensive profile, "
        "identify major skill matches, "
        "and extract relevant information that aligns with the job description."
    ),
    expected_output=(
        "A detailed report highlighting matched skills, missing skills, and relevant user information "
        "that represents a tailored user profile to a job description."
    ),
    agent=skill_matcher,
    dependencies=[research_task, profile_task],  # Ensures this task runs after research and profile tasks
    async_execution=False
)

# Initialize Crew with all agents and tasks
skill_matching_crew = Crew(
    agents=[
        researcher,
        profiler,
        skill_matcher
    ],
    tasks=[
        research_task,
        profile_task,
        skill_matching_task
    ],
    verbose=True
)

# Define inputs for the Crew
skills_inputs = {
    'job_posting_url': 'https://jobs.lever.co/AIFund/6c82e23e-d954-4dd8-a734-c0c2c5ee00f1?lever-origin=applied&lever-source%5B%5D=AI+Fund',
    'linkedin_profile_url': 'https://www.linkedin.com/in/matteo-steinbach-724547284/',
}

# Kickoff the Crew and collect results
result = skill_matching_crew.kickoff(inputs=skills_inputs)



# Now, send the results to the Flask app and the next Crew

# Example: Sending data to Flask app via HTTP POST
import requests
import json

flask_api_endpoint = 'http://localhost:5000/api/skill-matching-result'  # Replace with your Flask endpoint

# Prepare the payload
payload = {
    'job_requirements': job_requirements,
    'user_profile': user_profile,
    'skill_matching_output': skill_matching_output
}

# Send the POST request to Flask
try:
    response = requests.post(flask_api_endpoint, json=payload)
    if response.status_code == 200:
        print("Successfully sent Skill Matching results to Flask app.")
    else:
        print(f"Failed to send data to Flask app. Status Code: {response.status_code}")
except Exception as e:
    print(f"Error sending data to Flask app: {e}")

