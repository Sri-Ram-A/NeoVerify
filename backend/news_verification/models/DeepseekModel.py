from groq import Groq

class DeepseekChat:
    def __init__(
            self, api_key, model="deepseek-r1-distill-llama-70b", 
            temperature=0.6, max_tokens=4096, top_p=0.95, 
            system_prompt="Reply: No System prompt given"
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
            result,summary = self._process_response(response)
            self.messages.append({"role": "assistant", "content": result})
            return result,summary
        except Exception as e:
            print(f"An error occurred: in executing deepseek {e}")
            return None,None

    def _process_response(self, response):
        result = ""
        summary= ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                result += chunk.choices[0].delta.content
        summary=result[result.find("</think>")+len("</think>"):]
        return result,summary

