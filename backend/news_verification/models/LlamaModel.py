from groq import Groq

class LlamaChat:
    def __init__(
            self, api_key, model="llama-3.1-8b-instant",
            temperature=1, max_tokens=1024, top_p=1,
            system_prompt="Reply:System Prompt not given"
            ):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def send_message(self, statement):
        try:
            self.messages.append({"role": "user", "content": statement})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True,
                stop=None,
            )
            result = self._process_response(response)
            self.messages.append({"role": "assistant", "content": result})
            return result
        except Exception as e:
            print(f"An error occurred in executing llama: {e}")
            return None

    def _process_response(self, response):
        result = ""
        for chunk in response:
            result += chunk.choices[0].delta.content or ""
        return result