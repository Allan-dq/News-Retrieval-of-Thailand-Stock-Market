# Thai Stock Market Chatbot

A simple web interface for querying Thai stock market data and news via a chatbot powered by a Python backend and Gemini/OpenAI.

## Features

- **Free-form Q&A** about Thai stocks via `/chat` endpoint  
- **Real-time SET Index** lookup via `/realtime_index` endpoint  
- **News-aware queries** combining latest headlines with user questions 
- **Markdown responses** rendered in browser using

## Tech Stack

- Frontend: HTML, CSS, JavaScript  
- Markdown parsing: marked.js  
- Backend: Python (FastAPI or Flask), OpenAI/Gemini API, requests  

## Requirements

- Python 3.8+  
- `pip install -r requirements.txt` (e.g., `fastapi`, `uvicorn`, `openai`, `requests`)

## Installation

1. **Clone repo**  
   ```bash
   git clone https://github.com/your-username/thai-stock-chatbot.git
   cd thai-stock-chatbot
2.	**Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3.	**Run the backend server**
   ```bash
   uvicorn chatbot_gemini:app --reload --host 127.0.0.1 --port 8000
```
4.	**Open the frontend**
    Open chatbot_ui.html in your browser.
