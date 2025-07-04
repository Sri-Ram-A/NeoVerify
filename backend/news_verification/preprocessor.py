class Description:
    def __init__(self,TAVILY_API_KEY,GEMINI_API_KEY,SERP_API_KEY):
        self.TAVILY_API = TAVILY_API_KEY
        self.GEMINI_API_KEY = GEMINI_API_KEY
        self.SERP_API_KEY = SERP_API_KEY

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
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]

    def _extract_urls_from_image(self, url, api_key=None, hl='en', country="in"):
        from serpapi import GoogleSearch

        if api_key is None:
            api_key = self.SERP_API_KEY

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
            if value not in [None, 'null', 'None']:
                if key == "text":
                    responses[key] = value

                elif key == "image":
                    responses[key] = self._extract_image_description(value)
                    print("Successful Image description extracted")
                
                elif key == "video":
                    video_result = self._extract_video_description_vision(value)
                    responses[key] = video_result["summary"]
                    print("Successful Video description extracted")
                
                elif key == "audio":
                    responses[key] = self._extract_audio_description(value)
                    print("Successful Audio description extracted")
                
                elif key == "url":
                    content = self._extract_content_from_url(value)
                    responses[key] = content["text"]
                    print("Successful URL description extracted")
                else:
                    raise ValueError(f"Unsupported input type: {key}")
        return responses 

