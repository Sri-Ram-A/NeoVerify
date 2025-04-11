from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import json

# Define the expected schema
class DebateResponse(BaseModel):
    status: int = Field(..., description="1 for continue debate, 0 for stop debate")
    gemini_reason: str = Field(..., description="your analysis")
    llama_reason: str = Field(..., description="evaluation of LLaMA's argument")
    deepseek_reason: str = Field(..., description="evaluation of DeepSeek's argument")
    questions:list[str] = Field(..., description="questions which require more sources and are in google search format")

class GeminiIntermediate:
    def __init__(
            self, api_key, model_name="gemini-2.0-flash",
            temperature=1, top_p=0.95, top_k=40, max_output_tokens=1024,
            system_prompt="Reply:No system prompt given"
        ):
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)
        self.chat = self.client.chats.create(model=self.model_name)
        self.config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p, top_k=top_k,
            max_output_tokens=max_output_tokens,
            system_instruction=[types.Part.from_text(text=system_prompt)],
            response_mime_type='application/json',
            response_schema=DebateResponse
        )

    def send_message(self, claim, llama_response, deepseek_response):
        prompt = f"""
        Debate Topic: {claim}
        LLaMA's Argument:{llama_response}
        DeepSeek's Argument:{deepseek_response}
        Provide your analysis in the required JSON format:
        """
        response = self.chat.send_message(prompt, config=self.config)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print("Could not convert to JSON, returning string response.")
            return response.text

    def get_history(self):
        history = []
        for message in self.chat.get_history():
            history.append(f'role - {message.role}: {message.parts[0].text}')
        return history
