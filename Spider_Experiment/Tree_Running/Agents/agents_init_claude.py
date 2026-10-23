import os
from anthropic import Anthropic

# Anthropic Claude API configuration
api_key = "your-claude-api-key-here"
os.environ['ANTHROPIC_API_KEY'] = api_key

class LlmAgentClaude:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='claude-3-sonnet-20240229',
            temperature=0
    ):
        self.messages = messages
        self.client = Anthropic(api_key=api_key)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature
        # Convert messages to Claude format (remove system messages from messages list)
        self.system_message = None
        self.claude_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                self.system_message = msg['content']
            else:
                self.claude_messages.append(msg)

    def run(self):
        if self.system_message:
            response = self.client.messages.create(
                model=self.model_name,
                messages=self.claude_messages,
                system=self.system_message,
                temperature=self.temperature,
                max_tokens=4096
            )
        else:
            response = self.client.messages.create(
                model=self.model_name,
                messages=self.claude_messages,
                temperature=self.temperature,
                max_tokens=4096
            )
        return response.content[0].text

    def environmental_feedback(self, feedback):
        self.system_message = feedback
        # Also add as a system message for compatibility
        self.messages.append({
            'role': 'system',
            'content': feedback
        })

    def continue_conversation(self, user_input):
        self.messages.append({
            'role': 'user',
            'content': user_input
        })
        self.claude_messages.append({
            'role': 'user',
            'content': user_input
        })
        assistant_response = self.run()
        self.messages.append({
            'role': 'assistant',
            'content': assistant_response
        })
        self.claude_messages.append({
            'role': 'assistant',
            'content': assistant_response
        })
        return assistant_response

class LlmAgentClaudeHaiku:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='claude-3-haiku-20240307',
            temperature=0
    ):
        self.messages = messages
        self.client = Anthropic(api_key=api_key)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature
        # Convert messages to Claude format (remove system messages from messages list)
        self.system_message = None
        self.claude_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                self.system_message = msg['content']
            else:
                self.claude_messages.append(msg)

    def run(self):
        if self.system_message:
            response = self.client.messages.create(
                model=self.model_name,
                messages=self.claude_messages,
                system=self.system_message,
                temperature=self.temperature,
                max_tokens=4096
            )
        else:
            response = self.client.messages.create(
                model=self.model_name,
                messages=self.claude_messages,
                temperature=self.temperature,
                max_tokens=4096
            )
        return response.content[0].text

    def environmental_feedback(self, feedback):
        self.system_message = feedback
        # Also add as a system message for compatibility
        self.messages.append({
            'role': 'system',
            'content': feedback
        })

    def continue_conversation(self, user_input):
        self.messages.append({
            'role': 'user',
            'content': user_input
        })
        self.claude_messages.append({
            'role': 'user',
            'content': user_input
        })
        assistant_response = self.run()
        self.messages.append({
            'role': 'assistant',
            'content': assistant_response
        })
        self.claude_messages.append({
            'role': 'assistant',
            'content': assistant_response
        })
        return assistant_response