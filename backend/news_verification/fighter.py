from system_prompts import *
import models
import os
from dotenv import load_dotenv
from colorama import Fore, Style, init
from tavily_search import tavily_search
from preprocessor import Description
import warnings
from loguru import logger
warnings.filterwarnings("ignore")
init()  # Initialize colorama

class ClaimFighter:
    def __init__(self):
        load_dotenv("api.key")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serp_key=os.getenv("SERP_API_KEY")
        if not self.groq_key or not self.gemini_key or not self.tavily_key:
            raise ValueError("Missing API Keys.")
        print("✅ All API keys are loaded successfully!")
        # Initialize model instances
        self.llama = models.LlamaChat(api_key=self.groq_key, system_prompt=LLAMA_SYSTEM_PROMPT)
        self.deepseek = models.DeepseekChat(api_key=self.groq_key, system_prompt=DEEPSEEK_SYSTEM_PROMPT)
        self.gemini_chat = models.GeminiChat(api_key=self.gemini_key, system_prompt=GEMINI_EXTRACTOR_SYSTEM_PROMPT)
        self.gemini_arbitrator = models.GeminiIntermediate(api_key=self.gemini_key, system_prompt=GEMINI_INTERMEDIATE_SYSTEM_PROMPT)
        self.output=dict()

    def extract_claims(self,message:dict)->dict:
        """
        INPUT
            message:str
        OUTPUT
            response :dict
                'claims':list[str] 
        '       questions':list[str]
        """
        logger.info("🔍 Extracting claims using Gemini...")
        chat_session = models.GeminiChat(api_key=self.gemini_key, system_prompt=GEMINI_EXTRACTOR_SYSTEM_PROMPT)
        response = chat_session.send_message(str(message))
        print(f"{Fore.MAGENTA}RESPONSE FROM CLAIM EXTRACTOR-GEMINI IS")
        print(response)
        Style.RESET_ALL
        return response

    def save_to_markdown(self, content, filename="static/claim_fighter_results.md", mode="a"):
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
        for idx, claim in enumerate(response[0]["claims"][:3]):
            print(f"\n{Fore.YELLOW}=== CLAIM ({claim}) ==={Style.RESET_ALL}")
            markdown_content += f"### Claim: {claim}\n\n"
            claim_key = "claim" + str(idx)
            self.output[claim_key] = {'claim': claim}

            llama_response = claim
            round_num = 1
            status = True

            while status:
                # DeepSeek's Turn
                _, deepseek_response = self.deepseek.send_message(llama_response)
                print(f"\n{Fore.BLUE}=== DEEPSEEK (Round {round_num}) ==={Style.RESET_ALL}")
                print(f"Response: {deepseek_response}")
                markdown_content += f"#### Round {round_num}\n\n"
                markdown_content += f"**DeepSeek Response:**\n\n```\n{deepseek_response}\n```\n\n"

                if deepseek_response in [None, 'None', '', ' ']:
                    deepseek_response = "I don't know what to reply, my token limits have exceeded."
                deepseek_response = f"Claim is: {claim}\nOpponent's response: {deepseek_response}"

                # Llama's Turn
                llama_response = self.llama.send_message(deepseek_response)
                print(f"\n{Fore.RED}=== LLAMA (Round {round_num}) ==={Style.RESET_ALL}")
                print(f"Response: {llama_response}")
                markdown_content += f"**Llama Response:**\n\n```\n{llama_response}\n```\n\n"
                llama_response = f"Claim is: {claim}\nOpponent's response: {llama_response}"

                # Gemini (Arbitrator)
                gemini_response = self.gemini_arbitrator.send_message(
                    claim=claim,
                    llama_response=llama_response,
                    deepseek_response=deepseek_response
                )
                print(f"\n{Fore.GREEN}=== GEMINI (Round {round_num}) ==={Style.RESET_ALL}")
                print(f"Response: {gemini_response}")
                markdown_content += f"**Gemini Arbitrator:**\n\n```\n{gemini_response}\n```\n\n"
                status = gemini_response.get("status", False)

                self.output[claim_key][f'round{round_num}'] = {
                    'deepseek_response': deepseek_response,
                    'llama_response': llama_response,
                    'gemini_response': gemini_response,
                    'tavily_response': None
                }

                # Fact-check with Tavily
                if gemini_response.get("questions"):
                    sources = {}
                    markdown_content += "**Fact-Check Sources:**\n\n"
                    for question in gemini_response["questions"][:2]:
                        tavily_resp = tavily_search(query=question, max_results=1, TAVILY_API_KEY=self.tavily_key)
                        sources[question] = tavily_resp
                        markdown_content += f"- **Question:** {question}\n"
                        markdown_content += f"- **Source:** {tavily_resp}\n\n"
                    if sources:
                        sources_text = "\n\n".join([f"- {q}: {sources[q]}" for q in sources])
                        source_context = f"\n\n🔍 **Fact-Checked Sources:**\n{sources_text}"
                        llama_response += source_context
                        self.output[claim_key][f'round{round_num}']['tavily_response'] = sources

                markdown_content += f"---\n\n"
                round_num += 1

        # Save the fight results to markdown
        self.save_to_markdown(markdown_content)

        import json
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(self.output, f, ensure_ascii=False, indent=4)

        print(f"{Fore.GREEN}✅ Debate results successfully saved to markdown and output.json{Style.RESET_ALL}")
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
            self.save_to_markdown(markdown_header, mode="w")

            # Process inputs
            logger.info("🧠 Preprocessing inputs...")
            desc = Description(self.tavily_key,self.gemini_key,self.serp_key)
            results = desc.process(inputs)
            self.output['inputs'] = inputs
            self.output['descr'] = results
            print(f"{Fore.CYAN}✔️ Successfully preprocessed everything{Style.RESET_ALL}")

            # Add preprocessed results to markdown
            preprocessed_md = "## Preprocessed Content\n\n"
            for key, value in results.items():
                print(f"{Fore.CYAN}Processed {key.upper()} input:{Style.RESET_ALL}\n{'-' * 40}\n{value}\n")
                preprocessed_md += f"### {key.upper()} Content\n\n```\n{value}\n```\n\n"
            preprocessed_md += "---\n\n"
            self.save_to_markdown(preprocessed_md)
            print("*" * 50)

            # Extract claims
            claims = self.extract_claims(results)
            claims_md = "## Extracted Claims\n\n"
            claims_md += f"```\n{claims}\n```\n\n"
            self.save_to_markdown(claims_md)

            # Run the debate
            self.fight(claims)

            print(f"\n{Fore.GREEN}🏁 Results saved to claim_fighter_results.md{Style.RESET_ALL}")

        except Exception as e:
            logger.exception("❌ An error occurred in run()")
            error_md = f"\n\n## Error\n\n```\n{str(e)}\n```\n"
            self.save_to_markdown(error_md)

if __name__ == "__main__":
    fighter = ClaimFighter()
    input_data = {
        "text": "Donald trump has purposefully increased tarrifs to show he is greater than other countries",
        #"image": r"../data/donaldTarrifs/donald.jpg",
        "video":None,
        "audio": r"../data/donaldTarrifs/donald_shrinked.mp3",
        "url": f"https://www.firstpost.com/explainers/donald-trump-liberation-day-tariff-90-day-pause-explained-13878689.html"
    }
    fighter.run(input_data)