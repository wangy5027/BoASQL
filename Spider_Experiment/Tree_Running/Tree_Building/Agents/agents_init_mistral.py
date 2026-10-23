import os
from mistralai import Mistral

# Mistral API configuration
api_key = "your-mistral-api-key-here"
os.environ['MISTRAL_API_KEY'] = api_key

class LlmAgentMistral:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='mistral-large-latest',
            temperature=0
    ):
        self.messages = messages
        self.client = Mistral(api_key=api_key)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature

    def run(self):
        response = self.client.chat.complete(
            model=self.model_name,
            messages=self.messages,
            temperature=self.temperature
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