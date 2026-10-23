import os
import google.generativeai as genai

# Google Gemini API configuration
api_key = "your-gemini-api-key-here"
os.environ['GOOGLE_API_KEY'] = api_key

class LlmAgentGemini:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='gemini-pro',
            temperature=0
    ):
        self.messages = messages
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model_name)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature
        # Convert messages to Gemini format (join into single prompt)
        self.conversation_history = []
        self._convert_messages_to_gemini_format()

    def _convert_messages_to_gemini_format(self):
        """Convert OpenAI-style messages to Gemini format"""
        self.conversation_history = []
        for msg in self.messages:
            if msg['role'] == 'system':
                self.conversation_history.append(f"System: {msg['content']}")
            elif msg['role'] == 'user':
                self.conversation_history.append(f"User: {msg['content']}")
            elif msg['role'] == 'assistant':
                self.conversation_history.append(f"Assistant: {msg['content']}")

    def run(self):
        # Join conversation history into a single prompt
        prompt = "\n".join(self.conversation_history) + "\nAssistant: "

        generation_config = genai.types.GenerationConfig(
            temperature=self.temperature
        )

        response = self.client.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text

    def environmental_feedback(self, feedback):
        self.messages.append({
            'role': 'system',
            'content': feedback
        })
        self._convert_messages_to_gemini_format()

    def continue_conversation(self, user_input):
        self.messages.append({
            'role': 'user',
            'content': user_input
        })
        self.conversation_history.append(f"User: {user_input}")

        assistant_response = self.run()

        self.messages.append({
            'role': 'assistant',
            'content': assistant_response
        })
        self.conversation_history.append(f"Assistant: {assistant_response}")

        return assistant_response

class LlmAgentGeminiFlash:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='gemini-1.5-flash',
            temperature=0
    ):
        self.messages = messages
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model_name)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature
        # Convert messages to Gemini format (join into single prompt)
        self.conversation_history = []
        self._convert_messages_to_gemini_format()

    def _convert_messages_to_gemini_format(self):
        """Convert OpenAI-style messages to Gemini format"""
        self.conversation_history = []
        for msg in self.messages:
            if msg['role'] == 'system':
                self.conversation_history.append(f"System: {msg['content']}")
            elif msg['role'] == 'user':
                self.conversation_history.append(f"User: {msg['content']}")
            elif msg['role'] == 'assistant':
                self.conversation_history.append(f"Assistant: {msg['content']}")

    def run(self):
        # Join conversation history into a single prompt
        prompt = "\n".join(self.conversation_history) + "\nAssistant: "

        generation_config = genai.types.GenerationConfig(
            temperature=self.temperature
        )

        response = self.client.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text

    def environmental_feedback(self, feedback):
        self.messages.append({
            'role': 'system',
            'content': feedback
        })
        self._convert_messages_to_gemini_format()

    def continue_conversation(self, user_input):
        self.messages.append({
            'role': 'user',
            'content': user_input
        })
        self.conversation_history.append(f"User: {user_input}")

        assistant_response = self.run()

        self.messages.append({
            'role': 'assistant',
            'content': assistant_response
        })
        self.conversation_history.append(f"Assistant: {assistant_response}")

        return assistant_response