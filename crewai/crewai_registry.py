# crewai/crewai_orchestrator.py

import importlib
from crewai_config import CREWAI_SETTINGS
import logging

# Initialize logging
logging.basicConfig(level=CREWAI_SETTINGS['log_level'])
logger = logging.getLogger(__name__)

# Import CrewAI components (assuming CrewAI has an Orchestrator class)
from crewai import Orchestrator

def main():
    # Initialize the orchestrator with the settings
    orchestrator = Orchestrator(
        agent_registry=CREWAI_SETTINGS['agent_registry'],
        communication_protocol=CREWAI_SETTINGS['communication_protocol'],
        task_queue=CREWAI_SETTINGS['task_queue']
    )
    
    # Start the orchestrator
    orchestrator.start()
    logger.info("CrewAI Orchestrator started successfully.")

if __name__ == "__main__":
    main()
