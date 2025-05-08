import streamlit as st
import requests
import json
import re

# Streamlit page configuration
st.set_page_config(page_title="News Recommendation System", layout="wide")

# Title
st.title("News Recommendation System")

# Predefined topics
topics = ["Technology", "War", "Industrial", "All", "Political", "Stocks"]

# State to store recommendations and errors
if "recommendations" not in st.session_state:
    st.session_state.recommendations = ""
if "error" not in st.session_state:
    st.session_state.error = ""

def validate_topic(topic: str) -> bool:
    """Validate the topic input."""
    # Allow letters, numbers, spaces, and common punctuation
    return bool(re.match(r'^[\w\s\-,.]+$', topic))

def fetch_recommendations(topic: str):
    """Fetch recommendations from the Flask API."""
    try:
        with st.spinner("Fetching recommendations..."):
            response = requests.post(
                "http://localhost:5000/recommend",
                json={"topic": topic},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                st.session_state.error = f"API Error: {data['error']}"
                st.session_state.recommendations = ""
            else:
                st.session_state.recommendations = data.get("recommendations", "No recommendations available")
                st.session_state.error = ""
    except requests.exceptions.ConnectionError:
        st.session_state.error = "Error: Unable to connect to the API. Please ensure the Flask API is running on http://localhost:5000."
        st.session_state.recommendations = ""
    except requests.exceptions.HTTPError as e:
        st.session_state.error = f"Error: HTTP {e.response.status_code} - {e.response.reason}"
        st.session_state.recommendations = ""
    except requests.exceptions.RequestException as e:
        st.session_state.error = f"Error: {str(e)}"
        st.session_state.recommendations = ""

# Styling for buttons
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        font-size: 16px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .custom-input {
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
    }
    .stSpinner > div {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# Topic selection buttons
st.subheader("Select a Topic")
cols = st.columns(3)  # Create a 3-column grid for buttons
for i, topic in enumerate(topics):
    with cols[i % 3]:
        if st.button(topic, key=topic):
            fetch_recommendations(topic.lower())

# Custom topic input
st.subheader("Suggest a Custom Topic")
custom_topic = st.text_input(
    "Enter a topic (e.g., cryptocurrency, space exploration)", 
    key="custom_topic", 
    placeholder="Type your topic here..."
)
if st.button("Get Custom Recommendations", key="custom_submit"):
    if custom_topic.strip():
        if validate_topic(custom_topic):
            fetch_recommendations(custom_topic.lower())
        else:
            st.session_state.error = "Invalid topic. Please use letters, numbers, spaces, or basic punctuation."
            st.session_state.recommendations = ""
    else:
        st.session_state.error = "Please enter a valid topic."
        st.session_state.recommendations = ""

# Display error message
if st.session_state.error:
    st.error(st.session_state.error)

# Display recommendations
if st.session_state.recommendations:
    st.subheader("Recommendations")
    st.markdown(st.session_state.recommendations, unsafe_allow_html=True)

# Instructions
st.write("Click a topic button or enter a custom topic to get news recommendations.")