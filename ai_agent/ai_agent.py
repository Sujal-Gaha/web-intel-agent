from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

DEFAULT_AI_AGENCY_MODEL = "openai/gpt-oss-20b"
GROQ_API_KEY = str(os.getenv("GROQ_API_KEY"))

class AIAgent:
    def __init__(self, file_path, model=DEFAULT_AI_AGENCY_MODEL):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = model
        self.file_path = file_path
        self.user_prompt = ""
        self.ai_responses = []
        self.all_content = ""
        self.__all_chunks = []
        
    def __get_prompt_from_user(self):
        return input("What would you like to ask about this website? \n> ")
        
    def __read_and_process_file(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.all_content = f.read()

    def __chunk_text(self, max_tokens=2000):
        chunk_size = max_tokens * 4
        for i in range(0, len(self.all_content), chunk_size):
            self.__all_chunks.append(self.all_content[i:i+chunk_size])
            
    def __generate_responses(self, new_prompt):
        responses = []
        for index, chunk in enumerate(self.__all_chunks, 1):
            print()
            print("=" * 170)
            print(f"Receiving response for chunk {index}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant that answers questions about a website's content."},
                    {"role": "user", "content": f"Website content:\n{chunk}\n\nUser question: {new_prompt}"}
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or ""
            responses.append(content)
            print(f"Received response for chunk {index}")
            print("=" * 170)

        return responses
            
    def __save_responses(self, prompt, responses):
        print("Saving Responses")
        ai_json = {
            "user_prompt": prompt,
            "ai_responses": responses
        }
        
        with open("data/output.json", "w", encoding="utf-8") as f_json:
            json.dump(ai_json, f_json, indent=4)
        print("Responses Saved")

    def process(self):
        self.__read_and_process_file()
        self.__chunk_text()
        
        while True:
            prompt = self.__get_prompt_from_user()
            responses = self.__generate_responses(prompt)
            self.__save_responses(prompt, responses)

            print("\n", "---" * 35,  " AI Responses "  , "---" * 35)
            
            for i, response in enumerate(responses, 1):
                print(f"\nResponse {i}:\n{response}\n")

            cont = input("Do you want to ask another question? (y/n): ").strip().lower()
            if cont != "y":
                print("Exiting...")
                break
