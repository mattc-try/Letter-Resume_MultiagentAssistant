# agents/agent_registry.py

from agents.content_generation_agent import ContentGenerationAgent
from agents.skill_matching_agent import SkillMatchingAgent
from agents.feedback_agent import FeedbackAgent
from agents.refinement_agent import RefinementAgent

AGENT_CLASSES = {
    'ContentGenerationAgent': ContentGenerationAgent,
    'SkillMatchingAgent': SkillMatchingAgent,
    'FeedbackAgent': FeedbackAgent,
    'RefinementAgent': RefinementAgent,
}
