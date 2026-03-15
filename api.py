# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from duckduckgo_search import DDGS
from google import genai
import os
from dotenv import load_dotenv  # Add this

load_dotenv()  # Add this - It loads your .env file into the environment!

app = FastAPI(title="News Intelligence API")

# The SDK will now automatically find the key from your .env file
client = genai.Client()

class ResearchQuery(BaseModel):
    event_name: str

def scrape_news(event_name: str):
    """Scrapes the latest news articles using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            # Grab the top 10 news snippets
            news_results = ddgs.news(event_name, max_results=10)
            if news_results:
                # Format the output clearly for the LLM
                return [f"Title: {n['title']}\nSnippet: {n['body']}\nSource: {n['source']}" for n in news_results]
            return []
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

@app.post("/research")
def research_event(query: ResearchQuery):
    news_data = scrape_news(query.event_name)
    
    if not news_data:
        raise HTTPException(status_code=404, detail="Could not find recent news on this event.")

    # Combine the scraped snippets into a single text block
    context = "\n\n".join(news_data)
    
    prompt = f"""
    You are a fast, highly accurate news intelligence agent. 
    Analyze the following recent news snippets for the event: '{query.event_name}'.
    Synthesize the information into a clean, well-structured executive briefing using bullet points.
    
    CONTEXT:
    {context}
    """

    try:
        # Using gemini-2.5-flash as it is exceptionally fast and cost-effective for summarization
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"event": query.event_name, "briefing": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn api:app --reload