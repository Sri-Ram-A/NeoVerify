from google import genai
from google.genai import types
from pydantic import BaseModel
import json

# https://ai.google.dev/gemini-api/docs/text-generation#multi-turn-conversations
# https://ai.google.dev/gemini-api/docs/text-generation#configuration-parameters
# https://ai.google.dev/gemini-api/docs/structured-output?lang=python#supply-schema-in-config

class Prompt(BaseModel):
    claims:list[str]
    questions:list[str]

class GeminiChat:
    def __init__(
            self, api_key, model_name="gemini-2.0-flash",
            temperature=1, top_p=0.95, top_k=40, max_output_tokens=1024,
            system_prompt="Reply:No system prompt given"
            ):
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)
        self.chat = self.client.chats.create(model=self.model_name)
        self.config =types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,top_k=top_k,
            max_output_tokens=max_output_tokens,
            system_instruction=[types.Part.from_text(text=system_prompt)],
            response_mime_type= 'application/json',
            response_schema= list[Prompt],
        )
    def send_message(self, message_text):
        # chat.send_message is inbuilt function of genai
        response = self.chat.send_message(message_text, config=self.config)
        try:
            return json.loads(response.text) 
        except json.JSONDecodeError:
            print("Could not convert to json, returning string")
            return response.text 
        
    def get_history(self):
        # chat.get_history is inbuilt function of genai
        history = []
        for message in self.chat.get_history():
            history.append(f'role - {message.role}: {message.parts[0].text}')
        return history

