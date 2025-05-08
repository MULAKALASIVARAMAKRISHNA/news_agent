
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Optional, Dict, Any
import requests
from pydantic import BaseModel
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
    """Fetches news articles from NewsData.io API based on user interests."""
    try:
        keywords = [k.strip() for k in interests.split(",")]
        query = " ".join(keywords[:3])  # Use first 3 keywords
        
        params = {
            "apikey": NEWS_API_KEY,
            "q": query,
            "language": "en",
            "size": 5
        }
        
        response = requests.get("https://newsdata.io/api/1/news", params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get("results", [])
        print(f"📰 Fetched {len(articles)} articles for query: {query}")
        return articles
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ News API HTTP Error: {str(e)} - Status Code: {e.response.status_code}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ News API Request Error: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Unexpected Error in fetch_news_articles: {str(e)}")
        return []

class RankInput(BaseModel):
    articles: List[Dict[str, Any]]
    interests: str

def rank_articles(input_data: RankInput) -> str:
    """Ranks and summarizes articles using Gemini."""
    try:
        if not input_data.articles:
            print("⚠️ No articles to rank")
            return "No articles found matching your interests."
        
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=GOOGLE_API_KEY
        )

        articles_text = "\n\n".join(
            f"Title: {art.get('title', 'No title')}\n"
            f"Source: {art.get('source_id', 'Unknown')}\n"
            f"Description: {art.get('description', '')[:200]}..."
            for art in input_data.articles[:5]
        )

        prompt = f"""
**User Interests**: {input_data.interests}

**Task**: Select the 3 most relevant articles and provide:
1. A concise summary
2. Why it might interest the user
3. The source

**Articles**:
{articles_text}

**Format as markdown**"""
        response = model.invoke(prompt)
        print("✅ Articles ranked successfully")
        return response.content
    
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)}")
        return f"Failed to generate recommendations due to: {str(e)}"

def extract_interests_node(state: AgentState) -> Dict[str, str]:
    """Extracts user interests using the tool."""
    interests = get_user_interests.invoke(state['interests'])
    print(f"🔎 Extracted interests: {interests}")
    return {"interests": interests}

def fetch_articles_node(state: AgentState) -> Dict[str, List[Dict[str, Any]]]:
    """Fetches articles using the tool."""
    articles = fetch_news_articles.invoke(state['interests'])
    return {"articles": articles}

def rank_node(state: AgentState) -> Dict[str, str]:
    """Generates recommendations using the tool."""
    try:
        input_data = RankInput(articles=state["articles"], interests=state["interests"])
        print(f"📊 Ranking articles for interests: {input_data.interests}")
        ranked = rank_articles(input_data)
        return {"recommendations": ranked}
    except Exception as e:
        print(f"❌ Rank Node Error: {str(e)}")
        return {"recommendations": f"Failed to generate recommendations due to: {str(e)}"}

# Build and compile the workflow
workflow = StateGraph(AgentState)
workflow.add_node("extract_interests", extract_interests_node)
workflow.add_node("fetch_articles", fetch_articles_node)
workflow.add_node("rank", rank_node)

workflow.set_entry_point("extract_interests")
workflow.add_edge("extract_interests", "fetch_articles")
workflow.add_edge("fetch_articles", "rank")
workflow.add_edge("rank", END)

app_graph = workflow.compile()

@app.route('/')
def home():
    """Root route for basic API information."""
    return jsonify({
        "message": "Welcome to the News Recommendation API",
        "endpoint": "POST /recommend",
        "example": {"topic": "technology"}
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    """Handle recommendation requests."""
    try:
        data = request.get_json()
        topic = data.get('topic')
        print(f"Received request with topic: {topic}")

        if not topic:
            print("⚠️ Missing topic in request")
            return jsonify({"error": "Missing required field: topic"}), 400

        print(f"Processing request for topic: {topic}")
        result = app_graph.invoke({"interests": topic})
        print(f"Result: {result}")
        
        return jsonify({
            "recommendations": result.get('recommendations', 'No recommendations available')
        })
    
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🌟 Starting News Recommendation API 🌟")
    app.run(debug=True, port=5000)
    
    
    
    # python flask_api.py for running this  file.
