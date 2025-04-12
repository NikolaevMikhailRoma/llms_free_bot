#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Главный модуль для запуска Telegram бота с интеграцией OpenRouter.
Этот бот позволяет пользователям выбирать языковые модели из OpenRouter и общаться с ними.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Загрузка данных из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Точка входа в приложение"""
    # Здесь мы сначала импортируем функцию main из бота, чтобы избежать 
    # циклических импортов и проблем с асинхронными функциями
    from src.bot.telegram_bot import main as bot_main
    
    logger.info("Запуск Telegram бота с интеграцией OpenRouter")
    # Вызываем функцию запуска бота напрямую
    await bot_main()

if __name__ == "__main__":
    # Проверяем наличие необходимых API ключей
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("Ошибка: TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        print("Пожалуйста, убедитесь, что файл .env содержит TELEGRAM_BOT_TOKEN")
        exit(1)
    
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("Ошибка: OPENROUTER_API_KEY не найден в переменных окружения")
        print("Пожалуйста, убедитесь, что файл .env содержит OPENROUTER_API_KEY")
        exit(1)
    
    # Запуск асинхронной функции main
    asyncio.run(main())
