import os
from groq import Groq

# Groq API configuration for Llama 3
api_key = "your-groq-api-key-here"
os.environ['GROQ_API_KEY'] = api_key

class LlmAgentLlama3:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='llama3-70b-8192',
            temperature=0
    ):
        self.messages = messages
        self.client = Groq(api_key=api_key)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature

    def run(self):
        response = self.client.chat.completions.create(
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

class LlmAgentLlama3_8B:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='llama3-8b-8192',
            temperature=0
    ):
        self.messages = messages
        self.client = Groq(api_key=api_key)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature

    def run(self):
        response = self.client.chat.completions.create(
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