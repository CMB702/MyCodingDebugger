# Telegram AI Coding Debugger

A Python 3.11+ Telegram bot that sends code or error reports to any OpenAI-compatible API and returns a structured diagnosis, corrected code, explanation, and improvement suggestions.

## Setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set `TELEGRAM_BOT_TOKEN`, `AI_API_KEY`, `AI_BASE_URL`, and `AI_MODEL`.
4. Start the bot: `python bot.py`

`AI_BASE_URL` accepts any OpenAI-compatible endpoint, such as `https://api.openai.com/v1`. Credentials are read only from `.env` or the environment, are never hardcoded, and are not logged.

## Use

- `/start` displays the welcome message and commands.
- Send source code, an error message, or both for automatic analysis.
- Use `/debug <code or error>` to submit an explicit debugging request.

The bot supports Python, JavaScript, TypeScript, C, C++, Java, HTML, CSS, SQL, PHP, C#, Go, and Rust. It asks the AI to infer other or ambiguous languages.

Requests are stored locally in SQLite (`debugger.db`) with the Telegram user ID, inferred language, and original submission. The database is ignored by Git.

## Deploy on Render (24/7)

The included `render.yaml` deploys this bot as a continuous Render Background Worker. Push this folder to a private GitHub repository, then in Render select **New > Blueprint**, connect the repository, and create the service. In Render's environment-variable screen, enter `TELEGRAM_BOT_TOKEN` and `AI_API_KEY` manually; do not place them in Git.

The configuration uses `https://openrouter.ai/api/v1` and `~openai/gpt-latest` by default. It also attaches a 1 GB persistent disk at `/var/data` so the SQLite history survives restarts and redeployments. Render documents that background workers run continuously, and persistent disks require a paid service plan. [Render background workers](https://render.com/docs/background-workers) · [Render persistent disks](https://render.com/docs/disks)
