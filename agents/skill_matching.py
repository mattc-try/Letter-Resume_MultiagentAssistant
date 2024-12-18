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

# Import necessary libraries
from crewai import Agent, Task  # Core CrewAI classes
from crewai_tools import ScrapeWebsiteTool, SerperDevTool  # Tools for scraping and searching


class SkillMatching:
    """
    A class to automate job analysis and skill matching using CrewAI.

    Features:
    - Analyzes job postings to extract requirements.
    - Creates comprehensive candidate profiles.
    - Matches candidate skills with job requirements.
    - Computes a matching score based on skill relevance.
    """

    def __init__(self):
        """
        Initialize SkillMatching class.
        Sets up scraping tools and creates agents for job analysis, profiling, and skill matching.
        """
        # Initialize scraping tool
        self.scrape_tool = ScrapeWebsiteTool()

        # Initialize agents
        self.researcher = self._create_researcher_agent()
        self.profiler = self._create_profiler_agent()
        self.skill_matcher = self._create_skill_matcher_agent()

    def _create_researcher_agent(self):
        """
        Create a job researcher agent to extract job requirements.
        """
        return Agent(
            role="Job Researcher",
            goal="Analyze job postings to extract key skills, experiences, and qualifications required.",
            tools=[self.scrape_tool],
            verbose=True,
            backstory=(
                "As a Job Researcher, your expertise in analyzing job postings helps pinpoint the necessary "
                "qualifications and skills sought by employers."
            )
        )

    def _create_profiler_agent(self):
        """
        Create a profiler agent to compile comprehensive professional profiles.
        """
        return Agent(
            role="Personal Candidate Profiler",
            goal="Compile comprehensive professional profiles to help candidates stand out in the job market.",
            tools=[self.scrape_tool],
            verbose=True,
            backstory=(
                "Using analytical skills, the agent synthesizes candidate data to build a detailed and impactful profile."
            )
        )

    def _create_skill_matcher_agent(self):
        """
        Create a skill matcher agent to compare candidate profiles with job requirements.
        """
        return Agent(
            role="Skill Matcher",
            goal="Match user's skills, education, and work experience with job requirements.",
            verbose=True,
            backstory=(
                "Analyze job requirements and user profiles to identify matches and gaps, providing actionable insights."
            )
        )

    def _create_research_task(self):
        """
        Define a task to extract job requirements from a job posting.
        """
        return Task(
            description=(
                "Scrape the job posting URL {job_posting_url} provided to extract key skills, experiences, and qualifications."
            ),
            expected_output="A structured list of job requirements, including necessary skills, qualifications, and experiences.",
            agent=self.researcher,
            async_execution=True
        )

    def _create_profile_task(self):
        """
        Define a task to compile a candidate's professional profile using provided data.
        """
        return Task(
            description=(
                "Compile a detailed professional profile using optional user website ({user_website}), "
                "personal write-up ({user_writeup}), education ({edu}), and work experience ({work_experience})."
            ),
            expected_output="A comprehensive profile document that includes skills, experiences, and contributions.",
            agent=self.profiler,
            async_execution=True
        )

    def _create_skill_matching_task(self):
        """
        Define a task to compare job requirements with a candidate's profile.
        """
        return Task(
            description=(
                "Using job requirements and the user's profile, identify matching skills and missing skills. "
                "Format: MATCHING_SKILL_[importance] or MISSING_SKILL_[importance] (leave the brackets eg: MATCHING_SKILL_[HIGH]) where importance can be LOW, HIGH, or CRITICAL. "
                "Do not forget the [] brackets around the importance level, They need to be there."
            ),
            expected_output=(
                "A detailed report highlighting matched skills, missing skills, and tailored suggestions."
            ),
            agent=self.skill_matcher,
            dependencies=[self._create_research_task(), self._create_profile_task()],
            async_execution=False
        )

    def compute_score(self, skill_matching_output):
        """
        Compute a score based on matching and missing skills.

        Args:
            skill_matching_output (str): Output containing MATCHING_SKILL and MISSING_SKILL entries.

        Returns:
            float: A score representing the percentage of matched skills.
        """
        matching_skills = []
        missing_skills = []

        # Weight mapping for importance levels
        weight_map = {
            'LOW': 1,
            'HIGH': 2,
            'CRITICAL': 3
        }

        # Parse each line to identify and extract skill importance
        for line in skill_matching_output.split('\n'):
            line = line.strip()
            if 'MATCHING_SKILL_' in line or 'MISSING_SKILL_' in line:
                start = line.find('[')
                end = line.find(']')
                if start != -1 and end != -1:
                    importance = line[start + 1:end]
                    if importance in weight_map:
                        weight = weight_map[importance]
                        if 'MATCHING_SKILL_' in line:
                            matching_skills.append(weight)
                        elif 'MISSING_SKILL_' in line:
                            missing_skills.append(weight)

        # Calculate total and compute score
        total_weight = sum(matching_skills) + sum(missing_skills)
        if total_weight == 0:  # Avoid division by zero
            return 0

        score = (sum(matching_skills) / total_weight) * 100
        return round(score, 2)
