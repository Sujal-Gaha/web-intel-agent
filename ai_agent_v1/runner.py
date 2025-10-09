from pathlib import Path
from .ai_agent_v1 import AIAgentV1

def run_ai_agent(directory: str):
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"The specified path does not exist: {directory}")

    agent = AIAgentV1(file_path=str(path))
    agent.process()
