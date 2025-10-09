from ai_agent_base import BaseAIAgent
import ollama, json, os
from utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_OLLAMA_MODEL = "deepseek-r1:14b"

class AIAgentV1(BaseAIAgent):
    def __init__(self, file_path, model=DEFAULT_OLLAMA_MODEL):
        super().__init__(file_path, model)
        self.all_content = ""
        self.__all_chunks = []

    def _read_and_process_file(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.all_content = f.read()

    def _chunk_text(self, max_tokens=32000):
        chunk_size = max_tokens * 4
        if len(self.all_content) <= chunk_size:
            self.__all_chunks = [self.all_content]
        else:
            for i in range(0, len(self.all_content), chunk_size):
                self.__all_chunks.append(self.all_content[i:i+chunk_size])

    def _generate_responses(self, user_prompt):
        responses = []
        for chunk in self.__all_chunks:
            prompt = (
                f"You are an assistant that answers questions about a website.\n"
                f"Website content:\n{chunk}\n\n"
                f"User question: {user_prompt}"
            )
            result = ollama.generate(model=self.model, prompt=prompt, stream=False)
            responses.append(result.get("response", ""))
        return responses

    def _save_responses(self, prompt, responses):
        os.makedirs("data", exist_ok=True)
        with open("data/output_v1.json", "w", encoding="utf-8") as f:
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

    # def process(self):
    #     self.__read_and_process_file()
    #     self.__chunk_text()

    #     while True:
    #         prompt = self.__get_prompt_from_user()
    #         responses = self.__generate_responses(prompt)
    #         self.__save_responses(prompt, responses)

    #         print("\n--- AI Responses ---")
    #         for i, response in enumerate(responses, 1):
    #             print(f"\n[Response {i}]\n{response}\n")

    #         cont = input("Do you want to ask another question? (y/n): ").strip().lower()
    #         if cont != "y":
    #             logger.info("Exiting program...")
    #             break
