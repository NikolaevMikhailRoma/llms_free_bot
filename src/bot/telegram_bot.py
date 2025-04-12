#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot implementation that integrates with OpenRouter API.

This module provides an asynchronous Telegram bot that allows users to
chat with various language models available through the OpenRouter API.
Users can select models, engage in conversations, and manage chat histories.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import sys
import os

# Add root directory to PATH for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.api.openrouter_api import OpenRouterClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenRouter client (will be created when bot starts)
openrouter_client = None

# User session storage (in-memory for simplicity)
user_sessions = {}

# Model storage (global for simplicity)
model_storage = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f'Hello, {user.first_name}! I\'m a chat bot using models from OpenRouter. '
        f'Use /models to select a model for chatting.'
    )
    
    # Add welcome message with feature description
    await update.message.reply_text(
        'I can help you chat with various language models. '
        'I have the following features:\n'
        '• Choose from 10 popular free models on OpenRouter\n'
        '• Save conversation history for context\n'
        '• Reset conversation history when needed\n\n'
        'To begin, type /models and select a model from the list.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when the command /help is issued."""
    await update.message.reply_text(
        'Available commands:\n'
        '/start - Start the bot and get welcome message\n'
        '/help - Show this help message\n'
        '/models - Select a model for chatting\n'
        '/reset - Clear conversation history'
    )

async def display_models(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0) -> None:
    """Display available models for selection with pagination."""
    # For callback queries, we need to handle differently
    is_callback = isinstance(update, Update) and update.callback_query
    
    # Get the appropriate message object
    message = update.callback_query.message if is_callback else update.message
    
    if not is_callback:
        await message.reply_text('Fetching available models...')
    
    try:
        # Get all free models from OpenRouter
        global openrouter_client
        free_models = await openrouter_client.get_free_models()
        
        if not free_models:
            if is_callback:
                await update.callback_query.answer("No models found")
                await update.callback_query.edit_message_text('Could not find any free models. Please try again later.')
            else:
                await message.reply_text('Could not find any free models. Please try again later.')
            return
        
        # Save all models to global storage
        global model_storage
        model_storage = {model['id']: model for model in free_models}
        
        # Calculate pagination
        models_per_page = 5
        total_models = len(free_models)
        total_pages = (total_models + models_per_page - 1) // models_per_page  # Ceiling division
        
        # Ensure page is in valid range
        page = max(0, min(page, total_pages - 1))
        
        # Get models for current page
        start_idx = page * models_per_page
        end_idx = min(start_idx + models_per_page, total_models)
        current_page_models = free_models[start_idx:end_idx]
        
        # Create keyboard with model options
        keyboard = []
        for i, model in enumerate(current_page_models):
            # Add 🆓 emoji for completely free models
            model_name = model['name']
            if model.get("is_free", False):
                model_name = f"🆓 {model_name}"
                
            keyboard.append([
                InlineKeyboardButton(model_name, callback_data=f"model:{model['id']}")
            ])
        
        # Add navigation buttons
        nav_buttons = []
        
        # Previous page button
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"page:{page-1}"))
        
        # Page indicator
        nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
        
        # Next page button
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"page:{page+1}"))
        
        # Add navigation row
        keyboard.append(nav_buttons)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Modify text to include page info and total model count
        select_text = f'Available models ({total_models} total) - Page {page+1}/{total_pages}:\n\nSelect a model to chat with:'
        
        # Edit or send message based on context
        if is_callback:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(select_text, reply_markup=reply_markup)
        else:
            await message.reply_text(select_text, reply_markup=reply_markup)
    
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        if is_callback:
            await update.callback_query.answer("Error loading models")
            await update.callback_query.edit_message_text(f'Error retrieving models: {str(e)}')
        else:
            await message.reply_text(f'Error retrieving models: {str(e)}')

async def page_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pagination navigation for model selection."""
    query = update.callback_query
    
    # "noop" callback does nothing 
    if query.data == "noop":
        await query.answer("Current page info")
        return
    
    # Extract page number from callback data
    page = int(query.data.split(':')[1])
    
    # Display models for the selected page
    await display_models(update, context, page=page)

async def model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle model selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    # Extract model ID from callback data
    model_id = query.data.split(':')[1]
    user_id = update.effective_user.id
    
    # Initialize user session if it doesn't exist
    if user_id not in user_sessions:
        user_sessions[user_id] = {"chat_history": []}
    
    # Set selected model
    user_sessions[user_id]["selected_model"] = model_id
    
    # Get model name from global storage
    model_name = "selected model"
    if model_id in model_storage:
        model_name = model_storage[model_id]['name']
        if model_storage[model_id].get("is_free", False):
            model_name = f"🆓 {model_name}"
    
    await query.edit_message_text(f'You selected model: {model_name}\n\nYou can now start chatting. Just send a message.')

async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset chat history for user."""
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        user_sessions[user_id]["chat_history"] = []
    
    await update.message.reply_text('Chat history has been reset. You can continue chatting with your selected model.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and generate responses using the selected model."""
    user_id = update.effective_user.id
    
    # Check if user has selected a model
    if user_id not in user_sessions or "selected_model" not in user_sessions[user_id]:
        await update.message.reply_text('Please select a model first using the /models command')
        return
    
    # Get user message
    user_message = update.message.text
    selected_model = user_sessions[user_id]["selected_model"]
    
    # Add user message to chat history
    user_sessions[user_id]["chat_history"].append({
        "role": "user",
        "content": user_message
    })
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Generate response from the model
        global openrouter_client
        response = await openrouter_client.generate_response(
            selected_model,
            user_message,
            user_sessions[user_id]["chat_history"][:-1]  # Exclude the last message
        )
        
        # Add model response to chat history
        user_sessions[user_id]["chat_history"].append({
            "role": "assistant",
            "content": response
        })
        
        # Limit chat history to 10 most recent messages to avoid context overflow
        if len(user_sessions[user_id]["chat_history"]) > 10:
            user_sessions[user_id]["chat_history"] = user_sessions[user_id]["chat_history"][-10:]
        
        # Send response to user
        await update.message.reply_text(response)
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text(f'An error occurred while generating response: {str(e)}')

async def main() -> None:
    """Initialize and run the bot."""
    # Import asyncio inside the function
    import asyncio
    
    # Initialize OpenRouter client
    global openrouter_client
    openrouter_client = OpenRouterClient()
    
    # Get the token from environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Telegram bot token not found in environment variables")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Setup bot commands menu
    from telegram import BotCommand
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot and get a welcome message"),
        BotCommand("help", "Show usage instructions"),
        BotCommand("models", "Select a free model for conversation"),
        BotCommand("reset", "Clear conversation history")
    ])
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("models", display_models))
    application.add_handler(CommandHandler("reset", reset_chat))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(model_selection, pattern=r'^model:'))
    application.add_handler(CallbackQueryHandler(page_navigation, pattern=r'^page:'))
    application.add_handler(CallbackQueryHandler(page_navigation, pattern=r'^noop$'))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("Bot is running. Press Ctrl+C to stop.")
    
    # Run the bot until pressing Ctrl-C
    # In the new version of python-telegram-bot, the idle method is directly in asyncio
    try:
        # Use asyncio.Event to block the main thread until completion
        stop_event = asyncio.Event()
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        # Properly stop the application when Ctrl+C is pressed
        logger.info("Shutting down the bot...")
    finally:
        # Close OpenRouter client session
        if openrouter_client:
            logger.info("Closing OpenRouter client...")
            await openrouter_client.close()
        
        # Stop the application
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
