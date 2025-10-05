from pathlib import Path
from .ai_agent import AIAgent

def run_ai_agent(directory: str):
    """Run the AI Agent on a given directory or file."""
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"The specified path does not exist: {directory}")

    agent = AIAgent(file_path=path)
    agent.process()
