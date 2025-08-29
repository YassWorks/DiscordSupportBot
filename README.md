# AI Discord Chatbot

I made this project to make it easier for new members of the IEEE CS chapter to get the hottest info about the new events and stuff like that. But really this can be used as a template for creating any AI powered Discord chatbot. Just tweak the tools and the system prompt and you'll be good to go!

### Tech used:

```md
- Python
- LangGraph         -> agent
- SQLite (async)    -> agent memory
- Render + Docker   -> deployment
```

## Usage

```text
/ask When and where will the Xtreeme event be held this year?
```

## Quick start

- Requirements: A Discord bot token, and a Cerebras API key.
- Copy `.env.example` to `.env` and fill in:

```env
DISCORD_TOKEN=your_discord_token
CEREBRAS_API_KEY=your_cerebras_api_key
```

### Run locally

```powershell
pip install -r requirements.txt
python .\main.py
```

### Run with Docker (optional)

```powershell
docker compose up --build
```

## Behavior & notes

- Slash command: `/ask <your question>` in your server where the bot is present.
- Guardrails: message length ≤ 1000 chars; per‑user rate limit ≈ 10 requests/hour.
- Memory: conversation state is saved to `backend/database/memory.sqlite` (async SQLite).
- Logs: daily log file in `logs/` (e.g., `YYYY-MM-DD.log`).
- Tuning: model and temperature live in `main.py`; system prompt in `backend/prompts/system_prompt.txt`.

## Directory


```
├─ main.py
├─ backend/
│  ├─ agent/
│  │  └─ agent.py
│  ├─ helpers/
│  │  └─ strip_thinking.py
│  ├─ prompts/
│  ├─ src/
│  │  ├─ get_response.py
│  │  └─ guardrails.py
│  └─ database/
├─ logs/
├─ .env.example
├─ requirements.txt
├─ pyproject.toml
├─ Dockerfile
└─ compose.yml
```