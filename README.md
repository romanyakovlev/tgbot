# Telegram Recipe Bot

This project provides a simple Telegram bot for storing recipes. It relies on SQLite for data storage and uses the aiogram framework.

## Quick start with Docker Compose

1. Create a `.env` file next to `docker-compose.yml` and define `API_TOKEN` and optional `ADMIN_LOGINS` variables.
2. Build and run the container:

```bash
docker-compose up --build
```

The bot will start polling Telegram inside the container.

## Running with Python and `venv`

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Export environment variables and run the bot:

```bash
export API_TOKEN=<your_bot_token>
export ADMIN_LOGINS='["12345", "67890"]'
python main.py
```

The database will be stored in `recipes.db` in the project directory.
