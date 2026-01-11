import os
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def fetch_url_content(url):
    """
    Helper to scrape text from a URL.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long (Gemini has limits, though high)
        return text[:10000] 
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

def summarize_content(url):
    """
    1. Scrapes URL
    2. Calls Gemini to summarize and tag
    Returns dict: {'summary': str, 'tags': str}
    """
    content = fetch_url_content(url)
    
    if not content:
        return {'summary': "Could not access this URL (Privacy or Security restriction).", 'tags': "error"}

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            f"Here is the text content of a website:\n\n{content}\n\n"
            "Please perform two tasks:\n"
            "1. Write a concise summary (max 2 sentences).\n"
            "2. Generate up to 5 relevant keywords/tags.\n"
            "Return the response ONLY as a raw JSON object with keys 'summary' and 'tags'. "
            "Tags should be a single string separated by commas."
            "Example: {\"summary\": \"This is a news site...\", \"tags\": \"news, world, politics\"}"
        )

        response = model.generate_content(prompt)
        text_response = response.text
        
        # Clean markdown if present
        clean_text = text_response.replace('```json', '').replace('```', '').strip()
        
        data = json.loads(clean_text)
        return data
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {'summary': "AI generation failed.", 'tags': "ai-error"}