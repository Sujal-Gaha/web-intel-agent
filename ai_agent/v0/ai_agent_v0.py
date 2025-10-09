from ai_agent_base import BaseAIAgent
from groq import Groq
import json, os
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AIAgentV0(BaseAIAgent):
    def __init__(self, file_path, model="openai/gpt-oss-20b"):
        super().__init__(file_path, model)
        self.client = Groq(api_key=GROQ_API_KEY)
        self.all_content = ""
        self.__all_chunks = []

    def _read_and_process_file(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.all_content = f.read()

    def _chunk_text(self, max_tokens=2000):
        chunk_size = max_tokens * 4
        for i in range(0, len(self.all_content), chunk_size):
            self.__all_chunks.append(self.all_content[i:i+chunk_size])

    def _generate_responses(self, user_prompt):
        responses = []
        for chunk in self.__all_chunks:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant that answers questions about a website's content."},
                    {"role": "user", "content": f"Website content:\n{chunk}\n\nUser question: {user_prompt}"}
                ],
                temperature=0.2,
            )
            responses.append(response.choices[0].message.content or "")
        return responses

    def _save_responses(self, prompt, responses):
        with open("data/output_v0.json", "w", encoding="utf-8") as f:
            json.dump({"user_prompt": prompt, "responses": responses}, f, indent=4)

    def process(self):
        self._read_and_process_file()
        self._chunk_text()
        
        while True:
            question = input("Ask something about the site:\n> ")
            responses = self._generate_responses(question)
            self._save_responses(question, responses)
            
            print("\n--- AI Responses ---")
            for i, response in enumerate(responses, 1):
                print(f"\n[Response {i}]\n{response}\n")

            cont = input("Do you want to ask another question? (y/n): ").strip().lower()
            if cont != "y":
                logger.info("Exiting program...")
                break
