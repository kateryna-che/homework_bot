# Telegram Status Bot

Telegram Status Bot is a Python bot that checks an external education platform API and sends Telegram notifications when the review status of a submitted task changes.

This repository is kept as a portfolio automation project. It shows API polling, Telegram integration, environment variables, response validation, logging, and error handling.

## Main features

- Periodic API polling
- Telegram notifications
- Environment-based configuration
- Response structure validation
- Status parsing
- Error reporting to Telegram
- Rotating file logs

## Tech stack

- Python
- Requests
- python-telegram-bot
- python-dotenv
- Logging

## Environment variables

Create a `.env` file in the project root:

```env
PRACTICUM_TOKEN=your-platform-api-token
TELEGRAM_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

## Local setup

```bash
git clone https://github.com/kateryna-che/homework_bot.git
cd homework_bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python homework.py
```

## How it works

The bot checks the API every 10 minutes. If a new status appears, it formats a human-readable message and sends it to Telegram. If an error happens, the bot logs it and sends an error notification.

## Status

Portfolio project focused on automation, API integration, and defensive checks.
