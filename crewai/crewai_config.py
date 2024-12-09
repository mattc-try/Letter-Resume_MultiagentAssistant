# crewai/crewai_config.py

CREWAI_SETTINGS = {
    'agent_registry': 'agents/agent_registry.py',   # Path to agent registry
    'communication_protocol': 'json',              # Communication protocol (e.g., JSON)
    'task_queue': 'redis://localhost:6379/0',      # Task queue backend (e.g., Redis)
    'log_level': 'INFO',                            # Logging level
}
