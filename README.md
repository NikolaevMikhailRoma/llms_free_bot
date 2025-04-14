# Telegram OpenRouter LLM Bot

A Telegram bot that integrates with OpenRouter API to access various free language models. Users can select from popular free models and chat with them directly in Telegram.

## Features

1. Access to all free models from OpenRouter
2. Easy model selection via in-chat buttons (🆓 marks completely free models) 
3. Chat with selected models through Telegram
4. Chat history management with reset capability
5. Model list caching for improved performance
6. Asynchronous architecture for concurrent user support

## Project Structure

```
/
├── main.py                 # Bot entry point
├── .env                    # API keys configuration
├── requirements.txt        # Project dependencies
├── data/                   # Data storage directory
│   └── models_cache.json   # OpenRouter models cache
├── src/                    # Source code
│   ├── __init__.py         # Package initialization
│   ├── api/                # API clients
│   │   ├── __init__.py     # API package initialization
│   │   └── openrouter_api.py  # OpenRouter API client
│   ├── bot/                # Bot modules
│   │   ├── __init__.py     # Bot package initialization
│   │   └── telegram_bot.py    # Telegram bot implementation
│   └── utils/              # Utility functions
│       └── __init__.py     # Utils package initialization
├── test/                   # Test suite
│   ├── __init__.py         # Test package initialization
│   ├── test_openrouter.py  # OpenRouter API tests
│   └── test_telegram.py    # Telegram Bot API tests
└── docs/                   # Documentation
```

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```
2. (optional) Install the virtual environment
2.1 Create environment
```
python -m venv .venv
```
3. Add api keys to .env file (create a new private file: .env)
```
OPENROUTER_API_KEY=<your_api_key>
TELEGRAM_BOT_TOKEN=<your_bot_token>
```


## Running

0. Activate virtual .venv

0.a (linux/mac)
```
source .venv/bin/activate
```
0.b (windows)
```
source .venv/Scripts/activate
```
1. Run OpenRouter API tests:
```
python test/test_openrouter.py
```

2. Run Telegram API tests:
```
python test/test_telegram.py
```

3. Start the Telegram bot:
```
python main.py
```

## Bot Usage

1. Find the bot on Telegram by searching for @FreeLLM_chatbot
2. Send `/start` to begin and get information about the bot
3. Use `/models` to select a language model (🆓 marks free models)
4. After selecting a model, simply send messages to chat
5. Use `/reset` to clear chat history
6. Use `/help` to view available commands

## API Documentation

The project uses the following APIs:
- [OpenRouter API](https://openrouter.ai/docs) - For LLM access
- [Telegram Bot API](https://core.telegram.org/bots/api) - For bot functionality

Access documentation in Cascade using these references:
- [@docs:openrouter-api](https://openrouter.ai/docs)
- [@docs:telegram-bot-api](https://core.telegram.org/bots/api)
