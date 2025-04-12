#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main module for launching Telegram bot with OpenRouter integration.
This bot allows users to select language models from OpenRouter and chat with them.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load data from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Application entry point"""
    # Here we first import the main function from the bot to avoid 
    # circular imports and problems with asynchronous functions
    from src.bot.telegram_bot import main as bot_main
    
    logger.info("Starting Telegram bot with OpenRouter integration")
    # Call the bot launch function directly
    await bot_main()

if __name__ == "__main__":
    # Check for required API keys
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Please make sure that the .env file contains TELEGRAM_BOT_TOKEN")
        exit(1)
    
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("Error: OPENROUTER_API_KEY not found in environment variables")
        print("Please make sure that the .env file contains OPENROUTER_API_KEY")
        exit(1)
    
    # Launch the asynchronous main function
    asyncio.run(main())
