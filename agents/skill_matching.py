import warnings
import os
from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

class SkillMatching:
    def __init__(self):
        # Initialize tools
        self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()

        # Initialize agents
        self.researcher = self._create_researcher_agent()
        self.profiler = self._create_profiler_agent()
        self.skill_matcher = self._create_skill_matcher_agent()

    def _create_researcher_agent(self):
        return Agent(
            role="Tech Job Researcher",
            goal="Analyze job postings to extract key skills, experiences, and qualifications required.",
            tools=[self.scrape_tool, self.search_tool],
            verbose=True,
            backstory=(
                "As a Job Researcher, your prowess in navigating and extracting critical "
                "information from job postings is unmatched. Your skills help pinpoint the necessary "
                "qualifications and skills sought by employers, forming the foundation for effective application tailoring."
            )
        )

    def _create_profiler_agent(self):
        return Agent(
            role="Personal Profiler for Engineers",
            goal="Compile comprehensive professional profiles to help candidates stand out in the job market.",
            tools=[self.scrape_tool, self.search_tool],
            verbose=True,
            backstory=(
                "Equipped with analytical prowess, you synthesize information from candidate profiles "
                "to craft professional profiles, laying the groundwork for tailored resumes."
            )
        )

    def _create_skill_matcher_agent(self):
        return Agent(
            role="Skill Matcher",
            goal="Match user's skills, education, and work experience with job requirements.",
            verbose=True,
            backstory=(
                "You analyze job requirements and the user's profile to identify skill matches and gaps, "
                "providing actionable insights for a tailored job application."
            )
        )

    def _create_research_task(self):
        return Task(
            description=(
                "Scrape the job posting URL {job_posting_url} provided to extract key skills, experiences, and qualifications "
                "required. Use the tools to gather content and identify and categorize the requirements."
            ),
            expected_output="A structured list of job requirements, including necessary skills, qualifications, and experiences.",
            agent=self.researcher,
            async_execution=True
        )

    def _create_profile_task(self):
        return Task(
    description=(
        "Compile a detailed personal and professional profile "
        "using scraping the website the user optionally provided: ({user_website}) and his personal write-up "
        "({user_writeup}). Utilize tools to extract and "
        "synthesize information from these sources."
    ),
    expected_output=(
        "A comprehensive profile document that includes skills, "
        "project experiences, contributions, interests, and "
        "communication style."
    ),
    agent=self.profiler,
    async_execution=True
)


    def _create_skill_matching_task(self):
        return Task(
            description=(
                "Using the job requirements and the user's comprehensive profile, identify major skill matches "
                "and extract relevant information that aligns with the job description."
            ),
            expected_output="A detailed report highlighting matched skills, missing skills, and tailored suggestions.",
            agent=self.skill_matcher,
            dependencies=[self._create_research_task(), self._create_profile_task()],
            async_execution=False
        )

