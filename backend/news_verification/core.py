from system_prompts import *
import models
import os
from dotenv import load_dotenv
from colorama import Fore, Style, init
from tavily_search import tavily_search
from preprocessor import Description
import warnings
warnings.filterwarnings("ignore")
init()  # Initialize colorama

class ClaimFighter:
    def __init__(self):
        load_dotenv("api.key")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        if not self.groq_key or not self.gemini_key or not self.tavily_key:
            raise ValueError("Missing API Keys.")
        print("✅ All API keys are loaded successfully!")
        # Initialize model instances
        self.llama = models.LlamaChat(api_key=self.groq_key, system_prompt=LLAMA_SYSTEM_PROMPT)
        self.deepseek = models.DeepseekChat(api_key=self.groq_key, system_prompt=DEEPSEEK_SYSTEM_PROMPT)
        self.gemini_chat = models.GeminiChat(api_key=self.gemini_key, system_prompt=GEMINI_EXTRACTOR_SYSTEM_PROMPT)
        self.gemini_arbitrator = models.GeminiIntermediate(api_key=self.gemini_key, system_prompt=GEMINI_INTERMEDIATE_SYSTEM_PROMPT)

    def extract_claims(self, message: dict) -> dict:
        # print(f"{Fore.LIGHTGREEN_EX}USER MESSAGE:")
        # print(message)
        response = self.gemini_chat.send_message(str(message))
        print(f"{Fore.MAGENTA}CLAIM EXTRACTOR RESPONSE:")
        print(response)
        Style.RESET_ALL
        return response
    
    def save_to_markdown(self, content, filename="claim_fighter_results.md", mode="a"):
        """
        Save content to a markdown file
        
        Args:
            content (str): Content to write to the file
            filename (str): Name of the markdown file
            mode (str): Write mode ('w' for write/overwrite, 'a' for append)
        """
        with open(filename, mode, encoding="utf-8") as md_file:
            md_file.write(content)

    def fight(self, response):
        markdown_content = "## Debate Results\n\n"
        
        for claim in response[0]["claims"]:
            print(f"\n{Fore.YELLOW}=== CLAIM ({claim}) ===")
            Style.RESET_ALL
            
            markdown_content += f"### Claim: {claim}\n\n"
            
            llama_response = claim
            round_num = 1
            status = True
            
            while status:
                # DeepSeek's Turn
                _, deepseek_response = self.deepseek.send_message(llama_response)
                print(f"\n{Fore.BLUE}=== DEEPSEEK (Round {round_num}) ===")
                print(f"Response:{Style.RESET_ALL} {deepseek_response}")
                
                markdown_content += f"#### Round {round_num}\n\n"
                markdown_content += f"**DeepSeek Response:**\n\n```\n{deepseek_response}\n```\n\n"
                
                if not deepseek_response or deepseek_response == "None":
                    deepseek_response = "I don't know what to reply, my token limits have exceeded."
                deepseek_response = f"Claim is: {claim}\nOpponent's response: {deepseek_response}"

                # Llama's Turn
                llama_response = self.llama.send_message(deepseek_response)
                print(f"\n{Fore.RED}=== LLAMA (Round {round_num}) ===")
                print(f"Response:{Style.RESET_ALL} {llama_response}")
                
                markdown_content += f"**Llama Response:**\n\n```\n{llama_response}\n```\n\n"
                
                llama_response = f"Claim is: {claim}\nOpponent's response: {llama_response}"

                # Gemini (Arbitrator)
                gemini_response = self.gemini_arbitrator.send_message(
                    claim=claim, 
                    llama_response=llama_response, 
                    deepseek_response=deepseek_response
                )
                print(f"\n{Fore.GREEN}=== GEMINI (Round {round_num}) ===")
                print(f"Response:{Style.RESET_ALL} {gemini_response}")
                
                markdown_content += f"**Gemini Arbitrator:**\n\n```\n{gemini_response}\n```\n\n"
                
                status = gemini_response.get("status", False)

                # Fact-check with Tavily
                if gemini_response.get("questions"):
                    sources = {}
                    markdown_content += f"**Fact-Check Sources:**\n\n"
                    
                    for question in gemini_response["questions"][0:2]:
                        tavily_resp = tavily_search(query=question, max_results=1, TAVILY_API_KEY=self.tavily_key)
                        sources[question] = tavily_resp
                        markdown_content += f"- **Question:** {question}\n"
                        markdown_content += f"- **Source:** {tavily_resp}\n\n"
                        
                    if sources:
                        sources_text = "\n\n".join([f"- {q}: {sources[q]}" for q in sources])
                        source_context = f"\n\n🔍 **Fact-Checked Sources:**\n{sources_text}"
                        llama_response += source_context
                
                markdown_content += f"---\n\n"
                round_num += 1
                break
                
        # Save the fight results to markdown
        self.save_to_markdown(markdown_content)
        return markdown_content

    def run(self, inputs: dict):
        try:
            # Initialize markdown file with header and user inputs
            markdown_header = "# ClaimFighter Results\n\n"
            markdown_header += "## User Inputs\n\n"
            for key, value in inputs.items():
                if value:
                    markdown_header += f"- **{key.upper()}**: {value}\n"
            markdown_header += "\n---\n\n"
            
            # Write initial content (overwrite any existing file)
            self.save_to_markdown(markdown_header, mode="w")
            
            # Process inputs
            desc = Description()
            results = desc.process(inputs)
            print("successfully preprocessed everything")
            
            # Add preprocessed results to markdown
            preprocessed_md = "## Preprocessed Content\n\n"
            for key, value in results.items():
                print(f"\nProcessed {key.upper()} input:\n{'-' * 40}\n{value}\n")
                preprocessed_md += f"### {key.upper()} Content\n\n"
                preprocessed_md += f"```\n{value}\n```\n\n"
            
            preprocessed_md += "---\n\n"
            self.save_to_markdown(preprocessed_md)
            print("*"*50)
            
            # Extract claims
            claims = self.extract_claims(results)
            claims_md = "## Extracted Claims\n\n"
            claims_md += f"```\n{claims}\n```\n\n"
            self.save_to_markdown(claims_md)
            
            # Run the debate
            self.fight(claims)
            
            print(f"\n{Fore.GREEN}Results saved to claim_fighter_results.md{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"[ERROR] {e}")
            # Also log the error to markdown file
            error_md = f"\n\n## Error\n\n```\n{str(e)}\n```\n"
            self.save_to_markdown(error_md)


class Description:
    def __init__(self):
        self.TAVILY_API = "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"
        self.GEMINI_API_KEY = "AIzaSyCS_W7p-BJrzYwU1_drQ1fZPVOQR7CAH6E"
        #AIzaSyDG8RTYMMHQKuz0i2PDPmpaCVJBwkeFPZ4
        self.API_KEY = "5ee4136c602d451fd46aa04f03948041f84f9d574bc84b1d03cd4cec9312d9c3"

    def _extract_image_description(self, image_path: str) -> str:
        from PIL import Image
        import google.generativeai as genai
        genai.configure(api_key=self.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        image = Image.open(image_path)
        response = model.generate_content(["Describe this image in detail.", image])
        return response.text

    def _extract_video_description_vision(self, video_path: str, frame_count=3) -> dict:
        import cv2
        from PIL import Image
        import google.generativeai as genai

        genai.configure(api_key=self.GEMINI_API_KEY)
        vision_model = genai.GenerativeModel('gemini-1.5-pro')
        text_model = genai.GenerativeModel('gemini-1.5-pro')

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = max(total_frames // frame_count, 1)

        descriptions = []
        for i in range(frame_count):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)

                response = vision_model.generate_content(["Describe this frame in detail:", pil_image])
                if response.text:
                    descriptions.append(response.text.strip())

        cap.release()
        combined_description = "\n".join(descriptions)

        try:
            summary_prompt = (
                "Summarize the following visual descriptions into 3–4 sentences. "
                "Focus on the main scene, activity, people, and mood:\n\n" + combined_description
            )
            summary_response = text_model.generate_content(summary_prompt)
            summary_text = summary_response.text.strip()
        except Exception as e:
            print(f"[ERROR: Gemini summarization failed] {e}")
            summary_text = combined_description[:300] + "..."

        return {
            "combined_description": combined_description,
            "summary": summary_text
        }

    def _extract_audio_description(self, audio_path: str) -> str:
        import whisper
        model = whisper.load_model("small")
        result = model.transcribe(audio_path)
        return result["text"]

    def _extract_urls_from_image(self, url, api_key=None, hl='en', country="in"):
        from serpapi import GoogleSearch

        if api_key is None:
            api_key = self.API_KEY

        params = {
            "api_key": api_key,
            "engine": "google_lens",
            "url": url,
            "country": country,
            "hl": hl
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        urls = [dictionary["link"] for dictionary in results.get("visual_matches", [])]
        return urls

    def _extract_content_from_url(self, url: str, source=None, is_text=False, is_image=False):
        import tldextract
        from newspaper import Article
        article = Article(url)
        article.download()
        article.parse()
        extracted = tldextract.extract(url)
        source = f"{extracted.domain}.{extracted.suffix}"

        info = {
            "url": url,
            "source": source,
            "title": article.title,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "top_image": article.top_image,
            "text": article.text
        }
        if is_image:
            info["media_type"] = "image"
        if is_text:
            info["media_type"] = "text"
        return info
    
    def process(self, input_dict):
        responses = {}
        for key, value in input_dict.items():
            if value:
                if key == "text":
                    responses[key] = value

                elif key == "image":
                    responses[key] = self._extract_image_description(value)
                
                elif key == "video":
                    video_result = self._extract_video_description_vision(value)
                    responses[key] = video_result["summary"]
                
                elif key == "audio":
                    responses[key] = self._extract_audio_description(value)
                
                elif key == "url":
                    content = self._extract_content_from_url(value)
                    responses[key] = content["text"]
                else:
                    raise ValueError(f"Unsupported input type: {key}")
                    if not responses:
                        raise ValueError("All input values are None.")
        return responses


if __name__ == "__main__":
    fighter = ClaimFighter()
    input_data = {
        "text": "Donald trump has purposefully increased tarrifs to show he is greater than other countries",
        "image": r"/workspaces/fantom_code/backend/data/donald.jpg",
        "video": None,
        "audio": r"/workspaces/fantom_code/backend/data/donaltrump(1) (mp3cut.net) (1).mp3",
        "url": f"https://www.firstpost.com/explainers/donald-trump-liberation-day-tariff-90-day-pause-explained-13878689.html"
    }
    fighter.run(input_data)