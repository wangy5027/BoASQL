import os
from huggingface_hub import InferenceClient

# Hugging Face API configuration
api_key = "your-huggingface-api-key-here"
os.environ['HF_API_KEY'] = api_key

class LlmAgentCodeLlama:
    def __init__(
            self,
            messages=[],
            type='text',
            model_name='codellama/CodeLlama-34b-Instruct-hf',
            temperature=0
    ):
        self.messages = messages
        self.client = InferenceClient(model=model_name, token=api_key)
        self.type = type
        self.model_name = model_name
        self.temperature = temperature

    def run(self):
        # Convert messages to conversation format
        prompt = self._format_messages_as_prompt()

        response = self.client.text_generation(
            prompt=prompt,
            temperature=self.temperature,
            max_new_tokens=2048,
            return_full_text=False
        )
        return response

    def _format_messages_as_prompt(self):
        """Format messages as a single prompt for CodeLlama"""
        prompt_parts = []
        for msg in self.messages:
            if msg['role'] == 'system':
                prompt_parts.append(f"System: {msg['content']}")
            elif msg['role'] == 'user':
                prompt_parts.append(f"User: {msg['content']}")
            elif msg['role'] == 'assistant':
                prompt_parts.append(f"Assistant: {msg['content']}")

        prompt_parts.append("Assistant: ")
        return "\n".join(prompt_parts)

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