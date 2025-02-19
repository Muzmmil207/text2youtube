import requests

from src.config import cfg
from src.logger import logger


class Openai:
    def __init__(self, prompt="", model="@cf/meta/llama-3-8b-instruct"):
        self.api_url = F"https://api.cloudflare.com/client/v4/accounts/{cfg.CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"
        self.api_key = cfg.CLOUDFLARE_API_KEY
        self.system_prompt = self.get_system_prompt(
            f"{cfg.OPENAI_PROMPTS_PATH}/{prompt}"
        )
        logger.info(f"API model initialized. Model: {model}. Prompt: {prompt}")

    @staticmethod
    def get_system_prompt(filename):
        with open(filename, encoding="UTF-8") as f:
            return "".join(f.readlines())

    def generate_message(self, content):
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": content},
        ]  # Set the system prompt

    def generate_response(self, content):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {'max_tokens': 1500, "messages": self.generate_message(content)}
        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            return data['result']['response']
        else:
            logger.error(
                f"API call failed with status code {response.status_code}: {response.text}"
            )
            return None


def run_openai_generation(input_data: str, prompt: str):
    model = Openai(prompt)
    return model.generate_response(input_data)
