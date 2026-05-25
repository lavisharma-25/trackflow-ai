import json
from openai import OpenAI
from app.prompts.system_prompt import SYSTEM_PROMPT


client = OpenAI()


class IntentParser:

    @staticmethod
    def parse(query: str):

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        return json.loads(content)