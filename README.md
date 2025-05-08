News Recommendation System
Welcome to the News Recommendation System! This project lets you find news articles based on topics you care about, like technology or politics. It uses a web interface to let you pick topics and shows you the best articles, summarized and ranked for you.

Backend: A Flask API that fetches news from NewsData.io and ranks articles using Google's Gemini model.
Frontend: A Streamlit web app where you can choose topics and see recommendations.

This guide will help you set up and run the project, either on your computer with Python or using Docker for a simpler setup.
Table of Contents

What This Project Does
What You Need
Project Files
Setting Up the Project
Option 1: Run with Python
Option 2: Run with Docker


Using the App
Fixing Common Problems
Want to Help?
License

What This Project Does

Choose Topics: Pick from preset topics (e.g., Technology, Stocks) or type your own (e.g., cryptocurrency).
Get News: The app finds recent news articles from NewsData.io.
Smart Ranking: Uses Google’s Gemini to pick the top 3 articles, summarize them, and explain why they match your interests.
Easy Interface: A web page where you click buttons or type topics to see results.
Health Check: The backend has a way to check if it’s working (/health endpoint).

What You Need

Python 3.7 or newer (for running with Python).
Docker and Docker Compose (for running with Docker; install Docker Desktop on Windows/Mac).
API Keys:
Sign up at NewsData.io for a news API key.
Get a Google API key for Gemini from Google Cloud Console.


A text editor (e.g., Notepad, VS Code) to create the .env file.
Command line (e.g., Command Prompt or PowerShell on Windows).

Project Files
Your project folder (News_Agents) should have these files:

flask_api.py: The backend that gets and ranks news.
streamlit_app.py: The web interface you use in a browser.
requirements.txt: Lists the Python packages needed.
Dockerfile.flask: Instructions to build the Flask backend for Docker.
Dockerfile.streamlit: Instructions to build the Streamlit frontend for Docker.
docker-compose.yml: Sets up both services in Docker.
.env: Stores your API keys (you’ll create this).
README.md: This file.

If you’re missing requirements.txt, Dockerfile.flask, Dockerfile.streamlit, or docker-compose.yml, ask for help to create them.
Setting Up the Project
Option 1: Run with Python
This method runs the app directly on your computer using Python.

Open Your Project Folder:

Go to C:\Users\asus\Desktop\News_Agents in a command prompt:cd C:\Users\asus\Desktop\News_Agents




Set Up a Virtual Environment:

Create a virtual environment to keep things tidy:python -m venv venv


Activate it (on Windows):venv\Scripts\activate

You’ll see (venv) in your prompt.


Install Required Packages:

Install the packages listed in requirements.txt:pip install -r requirements.txt




Create the .env File:

In the News_Agents folder, create a file named .env using a text editor.
Add your API keys:NEWS_API_KEY=your_newsdata_io_api_key
GOOGLE_API_KEY=your_google_api_key


Replace your_newsdata_io_api_key and your_google_api_key with your actual keys.
Save and close the file.


Run the App (see Running the Application below).


Option 2: Run with Docker
This method uses Docker to run the app in containers, which is easier to manage and ensures everything works the same way.

Check Docker is Installed:

Run these commands to confirm Docker is ready:docker --version
docker-compose --version


If not installed, download Docker Desktop and follow its setup instructions.


Create the .env File:

Same as above: Create .env in News_Agents with your API keys:NEWS_API_KEY=your_newsdata_io_api_key
GOOGLE_API_KEY=your_google_api_key




Update streamlit_app.py for Docker:

Open streamlit_app.py and add these lines near the top (after imports):import os
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://localhost:5000")


In the fetch_recommendations function, change:response = requests.post("http://localhost:5000/recommend", ...)

to:response = requests.post(f"{FLASK_API_URL}/recommend", ...)


This lets Streamlit find the Flask API in Docker.


Run the App (see Docker Execution below).


Running the Application
Local Execution (Python)

Start the Flask API:

In a command prompt, go to News_Agents and activate the virtual environment:cd C:\Users\asus\Desktop\News_Agents
venv\Scripts\activate


Run the API:python flask_api.py


Look for: 🌟 Starting News Recommendation API 🌟 and Running on http://127.0.0.1:5000.


Start the Streamlit App:

Open a second command prompt, go to News_Agents, and activate the virtual environment.
Run the app:streamlit run streamlit_app.py


Open http://localhost:8501 in a browser to see the interface.



Docker Execution

Build and Start the Containers:

In a command prompt, go to News_Agents:cd C:\Users\asus\Desktop\News_Agents


Build and run both services:docker-compose up --build


Wait for the build to finish and services to start. You’ll see logs for both Flask and Streamlit.


Access the App:

Open http://localhost:8501 in a browser for the Streamlit interface.
Check the Flask API:
http://localhost:5000/ (shows API info).
http://localhost:5000/health (shows {"status":"healthy"}).




Stop the App:

Press Ctrl+C in the command prompt.
Remove the containers:docker-compose down





Using the App

Open the Web Interface:
Go to http://localhost:8501 in a browser.


Pick a Topic:
Click a button like “Technology” or “Stocks”.
Or type a topic like “cryptocurrency” in the text box and click “Get Custom Recommendations”.


See Results:
Recommendations show up below, with summaries and why they match your topic.
If something goes wrong (e.g., bad API key), you’ll see an error message in red.

![image](https://github.com/user-attachments/assets/106888f0-414d-4df9-9965-47d083b1cb69)
![image](https://github.com/user-attachments/assets/142c6ad5-3063-42a7-adec-2c8eee841835)




Test the API Directly (optional):
In a command prompt, try:curl -X POST http://localhost:5000/recommend -H "Content-Type: application/json" -d '{"topic":"technology"}'


This should return a JSON response with recommendations.



Fixing Common Problems

The Web Interface Says It Can’t Connect:
Make sure the Flask API is running (python flask_api.py or Docker).
Test the API: Open http://localhost:5000/health in a browser (should show {"status":"healthy"}).
For Docker, check logs: docker-compose logs flask_api.


No News Articles Show Up:
Check your API keys in .env are correct.
Test NewsData.io:curl "https://newsdata.io/api/1/news?apikey=your_newsdata_io_api_key&q=technology&language=en"


Ensure your Google API key works for Gemini (check Google Cloud Console).
Try a common topic like “technology”.


App Won’t Start Because of Ports:
Check if ports 5000 or 8501 are in use:netstat -aon | findstr :5000
netstat -aon | findstr :8501


Stop other programs using these ports: taskkill /PID <pid> /F.
Or change ports in flask_api.py (e.g., port=5001) or docker-compose.yml.


Docker Build Fails:
Look at the error in the terminal.
Ensure all files (requirements.txt, Dockerfiles, etc.) are in the folder.
Check for package version issues in requirements.txt.


Error Messages in Logs:
Share the exact error from the Flask or Streamlit logs with whoever is helping you.



Want to Help?
If you’d like to improve this project:

Make a copy of the project (fork it on GitHub).
Create a new branch: git checkout -b my-improvement.
Make your changes and save: git commit -m "Added my improvement".
Share your changes: git push origin my-improvement.
Ask to add your changes via a pull request on GitHub.

License
This project uses the MIT License. You can use, modify, and share it freely. See the LICENSE file for details (create one if needed).
 
