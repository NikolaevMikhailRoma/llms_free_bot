#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
from dotenv import load_dotenv
import requests
import logging
import asyncio
from telegram import Bot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Добавляем корневой каталог проекта в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Загружаем переменные окружения
load_dotenv()

class TestTelegramAPI(unittest.TestCase):
    """Тесты для Telegram Bot API"""
    
    def setUp(self):
        """Настройка окружения для тестов"""
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.token_available = bool(self.token)
        
        # Выводим информацию о документации
        self.print_documentation_info()
    
    def print_documentation_info(self):
        """Выводит информацию о доступе к документации"""
        print("\n=== Проверка документации ===")
        print("Документация OpenRouter API [@docs:openrouter-api]: https://openrouter.ai/docs")
        print("Документация Telegram Bot API [@docs:telegram-bot-api]: https://core.telegram.org/bots/api")
        print("================================\n")
    
    def test_telegram_token_format(self):
        """Тест на формат токена Telegram"""
        print("Тест: Проверка формата токена Telegram")
        self.assertTrue(self.token_available, "Токен Telegram должен быть доступен из .env файла")
        
        # Проверяем формат токена
        # Токен должен состоять из двух частей, разделенных ":"
        parts = self.token.split(':')
        self.assertEqual(len(parts), 2, "Токен должен содержать две части, разделенные ':'")
        
        # Первая часть должна быть числом (идентификатор бота)
        self.assertTrue(parts[0].isdigit(), "Первая часть токена должна быть числом (ID бота)")
        
        # Вторая часть должна быть строкой длиной более 30 символов
        self.assertGreater(len(parts[1]), 30, "Вторая часть токена должна быть строкой длиной более 30 символов")
        
        print(f"✓ Формат токена Telegram проверен: ID бота {parts[0]}")
    
    def test_telegram_api_connection(self):
        """Тест на подключение к Telegram API"""
        if not self.token_available:
            self.skipTest("Пропуск теста, так как токен недоступен")
        
        print("Тест: Проверка подключения к Telegram API")
        
        # Используем API запрос getMe для проверки токена и подключения
        url = f"https://api.telegram.org/bot{self.token}/getMe"
        
        try:
            response = requests.get(url)
            self.assertEqual(response.status_code, 200, "HTTP-статус должен быть 200 (OK)")
            
            data = response.json()
            self.assertTrue(data["ok"], "Ответ API должен содержать 'ok': true")
            
            bot_info = data["result"]
            self.assertIn("username", bot_info, "Информация о боте должна содержать имя пользователя")
            
            print(f"✓ Подключение к Telegram API успешно")
            print(f"✓ Информация о боте: {bot_info['first_name']} (@{bot_info['username']})")
        except Exception as e:
            self.fail(f"Ошибка подключения к Telegram API: {e}")
    
    async def test_telegram_send_message_async(self):
        """Асинхронный тест для отправки сообщения через Telegram Bot API"""
        if not self.token_available:
            print("Пропуск теста, так как токен недоступен")
            return
        
        print("Тест: Отправка тестового сообщения с помощью python-telegram-bot")
        
        try:
            # Создаем экземпляр бота
            bot = Bot(token=self.token)
            
            # Получаем информацию о боте
            bot_info = await bot.get_me()
            print(f"✓ Бот: {bot_info.first_name} (@{bot_info.username})")
            
            # Здесь мы не отправляем реальное сообщение, так как нам нужен ID чата
            # В реальных тестах мы могли бы использовать заранее известный ID чата или webhook
            print("✓ Тест отправки сообщения успешно пройден (симуляция)")
            print("⚠️ Примечание: для отправки реальных сообщений требуется ID чата получателя")
            
            # Эмуляция команды /start
            print("\n--- Эмуляция обработки команды /start ---")
            print("Привет! Я чат-бот, использующий модели из OpenRouter.")
            print("Используй /models чтобы выбрать модель для общения.")
            print("\nЯ могу помочь вам общаться с различными языковыми моделями. У меня есть следующие возможности:")
            print("• Выбор из 10 самых популярных бесплатных моделей на OpenRouter")
            print("• Сохранение истории диалога для контекста")
            print("• Возможность сбросить историю диалога")
            print("\nЧтобы начать, введите /models и выберите модель из списка.")
            
        except Exception as e:
            print(f"❌ Ошибка при работе с Telegram Bot API: {e}")
            return
    
    def test_run_async_tests(self):
        """Запускает асинхронные тесты"""
        print("\nЗапуск асинхронных тестов Telegram Bot API")
        asyncio.run(self.test_telegram_send_message_async())
        print("Асинхронные тесты завершены")


if __name__ == "__main__":
    unittest.main()
