import os
from openai import OpenAI

api_key = os.environ["OPENAI_API_KEY"]
base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
os.environ['OPENAI_BASE_URL'] = base_url

class LlmAgent:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name=os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo-16k'),
            # model_name='gpt-4o',
            temperature=0
    ):
        self.messages = messages
        self.client = OpenAI()
        self.type = type
        self.model_name = model_name
        self.temperature = temperature

    def run(self):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            temperature=self.temperature,
            response_format={"type": self.type}
        )
        return response.choices[0].message.content

    def environmental_feedback(self, feedback):
        self.messages.append({
            'role': 'system',
            'content': feedback
        })

    def continue_conversation(self, user_input):
        self.messages.append({
            'role': 'user',
            'content': user_input
        })
        assistant_response = self.run()
        self.messages.append({
            'role': 'assistant',
            'content': assistant_response
        })

        return assistant_response