import os
from dotenv import load_dotenv
from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime, timedelta
import requests
from pydantic import BaseModel

from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate API keys
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY not found in environment variables")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

class AgentState(TypedDict):
    interests: Optional[str]
    articles: Optional[List[Dict[str, Any]]]
    recommendations: Optional[str]

@tool
def get_user_interests(input: str) -> str:
    """Extracts user interests from natural language input."""
    input = input.lower().replace("i'm interested in", "").replace("and", ",")
    return ", ".join([kw.strip() for kw in input.split(",") if kw.strip()])

@tool
def fetch_news_articles(interests: str) -> List[Dict[str, Any]]:
    """Fetches news articles from NewsData.io API based on user interests.
    Returns a list of article dictionaries or empty list if error occurs."""
    try:
        # Format query parameters
        keywords = [k.strip() for k in interests.split(",")]
        query = " ".join(keywords)  # Simple space-separated query
        
        # API endpoint and parameters
        url = "https://newsdata.io/api/1/news"
        params = {
            "apikey": NEWS_API_KEY,
            "q": query,
            "language": "en",
            "size": 5  # Limit results
        }
        
        # Make the API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check API response status
        if data.get("status") != "success":
            print(f"⚠️ API returned non-success status: {data.get('status')}")
            print(f"Message: {data.get('message', 'No message')}")
            return []
            
        return data.get("results", [])
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching news articles: {str(e)}")
        if hasattr(e, 'response') and e.response:
            try:
                error_details = e.response.json()
                print(f"API Error Details: {error_details}")
            except:
                print(f"API Response: {e.response.text}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return []

class RankArticlesInput(BaseModel):
    articles: List[Dict[str, Any]]
    interests: str

@tool(args_schema=RankArticlesInput)
def rank_articles(input_data: RankArticlesInput) -> str:
    """Ranks and summarizes the most relevant articles using Gemini.
    Takes a RankArticlesInput object with articles and interests.
    Returns formatted recommendations or error message."""
    try:
        if not input_data.articles:
            return "No recent articles found matching your interests."
        
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=GOOGLE_API_KEY
        )

        # Prepare article data for the prompt
        articles_text = "\n\n".join(
            f"Title: {art.get('title', 'No title')}\n"
            f"Source: {art.get('source_id', 'Unknown source')}\n"
            f"Description: {art.get('description', 'No description')}\n"
            f"Published: {art.get('pubDate', 'Unknown date')}\n"
            f"Link: {art.get('link', 'No URL')}"
            for art in input_data.articles[:10]  # Limit to 10 articles max
        )

        prompt = f"""
**User Interests**: {input_data.interests}

**Task**: From these news articles, select the 3-5 most relevant ones and provide:
1. A concise summary of each
2. Why it might interest the user
3. The publication date and source

**Articles**:
{articles_text}

**Format your response as markdown with clear headings for each article**
"""
        response = model.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    except Exception as e:
        print(f"❌ Error generating recommendations: {str(e)}")
        return "I couldn't generate recommendations due to a technical issue."

def extract_interests_node(state: AgentState) -> Dict[str, str]:
    """Extracts and cleans user interests."""
    interests = get_user_interests.invoke(state['interests'])
    print(f"🔎 Extracted interests: {interests}")
    return {"interests": interests}

def fetch_articles_node(state: AgentState) -> Dict[str, List[Dict[str, Any]]]:
    """Fetches articles based on interests."""
    articles = fetch_news_articles.invoke(state['interests'])
    print(f"📰 Found {len(articles)} articles")
    return {"articles": articles}

def rank_node(state: AgentState) -> Dict[str, str]:
    """Generates recommendations from articles."""
    ranked = rank_articles.invoke(RankArticlesInput(
        articles=state["articles"],
        interests=state["interests"]
    ))
    return {"recommendations": ranked}

# Build the workflow graph
graph = StateGraph(AgentState)
graph.add_node("extract_interests", extract_interests_node)
graph.add_node("fetch_articles", fetch_articles_node)
graph.add_node("rank", rank_node)

graph.set_entry_point("extract_interests")
graph.add_edge("extract_interests", "fetch_articles")
graph.add_edge("fetch_articles", "rank")
graph.add_edge("rank", END)

news_recommender = graph.compile()

if __name__ == "__main__":
    print("🌟 News Recommendation System 🌟")
    print("Example interests: 'technology', 'AI and climate change', 'space exploration'")
    
    while True:
        try:
            user_input = input("\nWhat topics are you interested in? (or 'quit' to exit)\n> ")
            
            if user_input.lower() in ('quit', 'exit'):
                print("Goodbye!")
                break
                
            if not user_input.strip():
                print("Please enter some interests.")
                continue
                
            print("\n⏳ Finding relevant news...")
            result = news_recommender.invoke({"interests": user_input})
            
            print("\n🔍 Your Personalized News Recommendations:")
            print("="*50)
            print(result['recommendations'])
            print("="*50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again with different interests.")