# TailorTalk Calendar Bot

TailorTalk is a conversational AI agent that helps you book, check, and cancel appointments via chat. It uses a simulated in-memory calendar for development and OpenRouter (free LLM API) for natural language understanding.

## Features
- Chat-based appointment booking, checking, and cancellation
- No Google Calendar or OAuth required (uses a simulated calendar)
- Powered by OpenRouter LLM (free API key)
- FastAPI backend, Streamlit frontend
- Modular, easy to deploy, and secure (API keys in .env)

## Project Structure
```
backend/
  app/
    agent.py           # Main agent logic (uses OpenRouter and fake_calendar)
    fake_calendar.py   # In-memory calendar simulation
    api.py             # FastAPI routes
    schemas.py         # Pydantic models
  requirements.txt    # Backend dependencies
frontend/
  app.py              # Streamlit chat UI
  requirements.txt    # Frontend dependencies
.env                  # API keys (not committed)
.gitignore            # Ignores .env, venv, etc.
README.md             # This file
```

## Setup Instructions
1. **Clone the repo**
2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. **Install frontend dependencies**
   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```
5. **Add your OpenRouter API key**
   - Copy `.env` template and add your key:
     ```
     OPENROUTER_API_KEY=sk-or-...
     ```
6. **Run the backend**
   ```bash
   cd ../backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
7. **Run the frontend**
   ```bash
   cd ../frontend
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```
8. **Chat with your bot!**
   - Open your browser to `http://localhost:8501`

## Deployment
- Use the provided Dockerfiles in `deployment/` for cloud deployment (Render, Railway, Fly.io, etc.)
- Make sure to set your environment variables securely in production.

## Security
- Never commit your `.env` or API keys.
- `.env` and `venv/` are already in `.gitignore`.

