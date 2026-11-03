# Thai Stock Market Chatbot

LLM-powered Q&A assistant for the Thai stock market (SET), built as a course project at Johns Hopkins University (Mar–May 2025). A FastAPI backend routes each question either to a live price lookup or to Gemini, and a lightweight browser UI renders the answers as Markdown.

## What it does

- **Intent routing**: questions such as "price of PTT" or "quote for AOT" are parsed into a SET ticker (`PTT.BK`) and answered with the latest close from Yahoo Finance; everything else goes to Gemini 2.0 Flash.
- **Multi-turn chat**: `POST /chat?session_id=...` keeps per-session conversation history so follow-up questions keep their context.
- **Live market data**: `GET /realtime_index` proxies the SET Marketplace real-time API for selected indices and symbols.
- **News collection**: `Scrap.ipynb` scrapes Bangkok Post business articles (URL, title, date, author, body) into `bangkokpost_business_articles.csv` for news retrieval experiments.
- **Browser UI**: `chatbot_ui.html` is a single-page chat client that renders responses with marked.js.

## Tech stack

Python · FastAPI · Uvicorn · Gemini API (REST) · yfinance · SET Marketplace API · requests · BeautifulSoup · HTML/CSS/JavaScript · marked.js

## Run locally

```bash
git clone https://github.com/Allan-dq/News-Retrieval-of-Thailand-Stock-Market.git
cd News-Retrieval-of-Thailand-Stock-Market
pip install -r requirements.txt

export GEMINI_API_KEY="your-gemini-key"
export SET_API_KEY="your-set-marketplace-key"   # only needed for /realtime_index

uvicorn chatbot_gemini:app --reload --host 127.0.0.1 --port 8000
```

Then open `chatbot_ui.html` in a browser.

## Endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/chat?query=...` | Single-turn question to Gemini |
| POST | `/chat?session_id=...` | Multi-turn chat; body `{"query": "..."}` |
| GET | `/realtime_index` | SET real-time index and stock data |

## Limitations

- Conversation history is kept in memory and is lost on restart.
- Ticker extraction is rule-based (trigger phrases), not model-based.
- The UI's news panel expects a `/realtime_news` endpoint that this backend does not implement yet.

## License

The code is released under the [MIT License](LICENSE). Scraped news text belongs to its original publishers and is not covered by this license.
