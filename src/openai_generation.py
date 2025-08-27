import os

from openai import OpenAI

from src.config import cfg
from src.logger import logger


class Openai:
    def __init__(self, key="", prompt="", model="gemini-2.5-pro"):
        self.client = OpenAI(api_key=key or os.getenv("OPENAI_API_KEY"))
        self.client.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        self.system_prompt = self.get_system_prompt(
            f"{cfg.OPENAI_PROMPTS_PATH}/{prompt}"
        )
        self.model = model
        logger.info(f"OpenAI model initialized. Model: {model}. Prompt: {prompt}")

    @staticmethod
    def get_system_prompt(filename):
        with open(filename, encoding="UTF-8") as f:
            return "".join(f.readlines())

    def generate_message(self, content):
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": content},
        ]  # Set the system prompt

    @staticmethod
    def get_text_from_response(response):
        completion_text = ""

        for event in response:
            if not event.choices:
                continue
            event_text = event.choices[0].delta.content
            if event_text:
                completion_text += event_text  # append the text

        return completion_text

    def generate_response(self, content):
        logger.info("Getting response...")
        messages = self.generate_message(content)  # Generate message for chat
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            max_tokens=1500,
        )
        return self.get_text_from_response(response)


def run_openai_generation(input_data: str, prompt: str):
    model = Openai(cfg.OPENAI_API_KEY, prompt)
    return model.generate_response(input_data)
