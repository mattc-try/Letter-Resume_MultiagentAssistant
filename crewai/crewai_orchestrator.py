
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

from agents.skill_matching import SkillMatching  # Import SkillMatcherAgent

# Extract outputs from the result
job_requirements = result.get('research_task', {}).get('output', [])
user_profile = result.get('profile_task', {}).get('output', {})
skill_matching_output = result.get('skill_matching_task', {}).get('output', {})


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

