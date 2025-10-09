from pathlib import Path
from .ai_agent_v0 import AIAgentV0

def run_ai_agent(directory: str):
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"The specified path does not exist: {directory}")

    agent = AIAgentV0(file_path=str(path))
    agent.process()
