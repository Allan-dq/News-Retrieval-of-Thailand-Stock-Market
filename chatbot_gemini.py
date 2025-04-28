from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import json
import logging
from typing import Optional
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ThaiStockChatbot")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = "AIzaSyAgol_MKg1rq8mJbJx3uMTYAlC1oYah8ZA"
SYSTEM_INSTRUCTION = "You are a financial assistant specializing in the Thai stock market."

SET_API_KEY = "0ab00c29-3df9-42b1-8325-56c15122f5e6"

conversation_history = {}

def call_gemini_api(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    try:
        data = response.json()
    except json.JSONDecodeError:
        logger.error("Invalid JSON response from Gemini API.")
        raise HTTPException(status_code=502, detail="Invalid response from Gemini API.")

    candidates = data.get("candidates", [])
    if not candidates:
        logger.error("No candidates returned from Gemini API.")
        raise HTTPException(status_code=502, detail="No response candidates from Gemini API.")

    candidate = candidates[0]
    content = candidate.get("content", {})
    parts = content.get("parts", [])
    if not parts:
        logger.error("No text parts found in the candidate response.")
        raise HTTPException(status_code=502, detail="Incomplete response from Gemini API.")
    response_text = parts[0].get("text", "No text in the first part.")
    return response_text

def get_stock_price_yf(symbol: str) -> str:
    try:
        ticker = yf.Ticker(symbol)
        # Get 1 day of historical data
        hist = ticker.history(period="1d")
        if hist.empty:
            return f"Sorry, I couldn’t fetch the price for {symbol} right now."
        
        # 'Close' column will have the last available trading day's close price
        current_price = hist["Close"].iloc[-1]
        
        # Return a response string
        return f"The current (last close) price of {symbol} is {current_price} THB."
    except Exception as e:
        logger.error(f"Error fetching stock price for {symbol}: {str(e)}")
        return f"An error occurred while fetching data for {symbol}."



def extract_symbol_after_trigger(query: str) -> Optional[str]:
    triggers = [
        "price of",
        "current price of",
        "stock price of",
        "quote for",
        "value of"
    ]
    text_lower = query.lower()
    for trigger in triggers:
        if trigger in text_lower:
            # everything after the trigger
            after_trigger = text_lower.split(trigger, 1)[1].strip()
            if not after_trigger:
                return None
            # first word from that remainder
            first_word = after_trigger.split()[0]
            # assume it's a Thai ticker, append .BK
            return first_word.upper() + ".BK"
    return None

@app.get("/")
def welcome():
    return {"message": "Welcome to the Thai Stock Market Chatbot (Gemini)!"}

@app.get("/chat")
def chat_with_gemini(query: str = Query(..., description="User's stock market question")):
    try:
        combined_text = f"{SYSTEM_INSTRUCTION}\nUser: {query}\nAssistant:"
        response_text = call_gemini_api(combined_text)
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Error in GET /chat: {str(e)}")
        return {"error": str(e)}

@app.post("/chat")
def chat_with_gemini_post(
    session_id: str = Query(..., description="Unique session identifier"),
    query: str = Body(..., embed=True, description="User's stock market question")
):
    try:
        # 1. Check if query includes a trigger phrase
        symbol = extract_symbol_after_trigger(query)
        if symbol:
            # 2. We found a symbol after the trigger => get stock price
            response_text = get_stock_price_yf(symbol)
            return {"session_id": session_id, "response": response_text}

        # 3. Otherwise fallback to Gemini
        history = conversation_history.get(session_id, SYSTEM_INSTRUCTION)
        updated_prompt = f"{history}\nUser: {query}\nAssistant:"
        response_text = call_gemini_api(updated_prompt)
        conversation_history[session_id] = f"{updated_prompt} {response_text}"
        return {"session_id": session_id, "response": response_text}
    except Exception as e:
        logger.error(f"Error in POST /chat for session {session_id}: {str(e)}")
        return {"error": str(e)}

@app.get("/realtime_index")
def get_set_realtime_data():
    url = "https://marketplace.set.or.th/api/public/realtime-data/stock"
    headers = {
        "api-key": SET_API_KEY
    }
    params = {
        "market": "SET,mai",
        "indexSector": "SET50,FINCIAL,BANK,INDUS-M",
        "securityType": "CS,DWC,DWP",
        "stockSymbol": "PTT,AOT,EGCO",
        "oddLotFlag": "false"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.status_code,
            "message": response.text
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
