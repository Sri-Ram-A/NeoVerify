def tavily_search(
    query: str,
    topic: str = "general",  # 'general' or 'news'
    search_depth: str = "advanced",  # 'basic' or 'advanced'
    chunks_per_source: int = 3,  # Max 3 (only for advanced search)
    max_results: int = 9,  # Max 20
    time_range: str = None,  # 'day', 'week', 'month', 'year', 'd', 'w', 'm', 'y'
    include_answer: bool = False,  # LLM-generated answer
    include_raw_content: bool = False,  # Parsed HTML content
    include_images: bool = False,  # Include image results
    include_image_descriptions: bool = False,  # Image descriptions (if include_images=True)
    include_domains: list = None,  # Domains to prioritize
    exclude_domains: list = None,  # Domains to exclude
    save_to_file: str = None,  # Save response to JSON file
    TAVILY_API_KEY:str =None
    ):
    url = "https://api.tavily.com/search"
    payload = {
        "query": query,
        "topic": topic,
        "search_depth": search_depth,
        "chunks_per_source": chunks_per_source,
        "max_results": max_results,
        "time_range": time_range,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content,
        "include_images": include_images,
        "include_image_descriptions": include_image_descriptions,
        "include_domains": include_domains or [],
        "exclude_domains": exclude_domains or [],
    }
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    import requests
    import json
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}, {response.text}")
    response_json = response.json()
    if save_to_file:
        with open(save_to_file, "w", encoding="utf-8") as file:
            json.dump(response_json, file, indent=4, ensure_ascii=False)
        print("Response saved to response.json")

    return response_json

