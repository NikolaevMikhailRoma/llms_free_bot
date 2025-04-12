#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import json
from dotenv import load_dotenv
import asyncio

# Добавляем корневой каталог проекта в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Импортируем клиент OpenRouter
from src.api.openrouter_api import OpenRouterClient

# Загружаем переменные окружения
load_dotenv()

# Используем IsolatedAsyncioTestCase для асинхронных тестов
class TestOpenRouterAPI(unittest.IsolatedAsyncioTestCase):
    """Тесты для API OpenRouter"""
    
    def setUp(self):
        """Настройка окружения для тестов"""
        self.client = OpenRouterClient()
        # Проверяем, доступен ли API ключ
        self.api_key_available = bool(os.getenv("OPENROUTER_API_KEY"))
        
        # Выводим информацию о документации
        self.print_documentation_info()
    
    async def asyncTearDown(self):
        """Закрываем сессию клиента после каждого теста"""
        if self.client:
            await self.client.close()

    def print_documentation_info(self):
        """Выводит информацию о доступе к документации"""
        print("\n=== Проверка документации ===")
        print("Документация OpenRouter API [@docs:openrouter-api]: https://openrouter.ai/docs")
        print("Документация Telegram Bot API [@docs:telegram-bot-api]: https://core.telegram.org/bots/api")
        print("================================\n")
    
    async def test_api_key_loaded(self):
        """Тест на загрузку API ключа из .env файла"""
        print("Тест: Проверка наличия API ключа OpenRouter")
        self.assertTrue(self.api_key_available, "API ключ должен быть доступен из .env файла")
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.assertIsNotNone(api_key, "API ключ должен быть загружен")
        self.assertTrue(api_key.startswith("sk-or-"), "API ключ должен иметь формат 'sk-or-*'")
        print(f"✓ API ключ OpenRouter успешно загружен: {api_key[:10]}...")
    
    async def test_get_available_models(self):
        """Тест на получение доступных моделей"""
        if not self.api_key_available:
            self.skipTest("Пропуск теста, так как API ключ недоступен")
        
        print("Тест: Получение списка всех моделей")
        # Используем await вместо asyncio.run()
        models = await self.client.get_available_models(use_cache=False)
        self.assertIsInstance(models, list, "get_available_models должен возвращать список")
        self.assertGreater(len(models), 0, "Должна быть хотя бы одна модель")
        
        # Проверка формата данных модели
        model = models[0]
        required_fields = ["id", "name"]
        for field in required_fields:
            self.assertIn(field, model, f"Модель должна содержать поле '{field}'")
        
        print(f"✓ Получено {len(models)} моделей")
        print(f"Пример модели: {model['name']} ({model['id']})")
    
    async def test_get_free_models(self):
        """Тест на получение бесплатных моделей"""
        if not self.api_key_available:
            self.skipTest("Пропуск теста, так как API ключ недоступен")
        
        print("Тест: Получение списка бесплатных моделей")
        # Используем await вместо asyncio.run()
        free_models = await self.client.get_free_models(limit=10)
        self.assertIsInstance(free_models, list, "get_free_models должен возвращать список")
        
        print(f"✓ Получено {len(free_models)} бесплатных моделей")
        
        # Проверяем, что в списке есть модели с "free" в названии
        free_in_name_count = sum(1 for model in free_models if model.get("is_free", False))
        print(f"✓ Моделей с 'free' в названии: {free_in_name_count}")
        
        # Выводим список бесплатных моделей
        print("\nСписок бесплатных моделей:")
        for i, model in enumerate(free_models, 1):
            is_free = "🆓" if model.get("is_free", False) else "  "
            print(f"{i}. {is_free} {model['name']} ({model['id']})")
    
    async def test_generate_response(self):
        """Тест на генерацию ответа от модели"""
        if not self.api_key_available:
            self.skipTest("Пропуск теста, так как API ключ недоступен")
        
        print("Тест: Генерация ответа от модели")
        
        # Получаем бесплатные модели (асинхронно с await)
        free_models = await self.client.get_free_models(limit=1)
        if not free_models:
            self.skipTest("Пропуск теста, так как нет доступных бесплатных моделей")
        
        model = free_models[0]
        print(f"✓ Используем модель: {model['name']} ({model['id']})")
        
        # Генерируем ответ (асинхронно с await)
        prompt = "Расскажи о себе в одном предложении как ИИ-ассистент."
        print(f"✓ Отправляем запрос: '{prompt}'")
        
        response = await self.client.generate_response(model['id'], prompt)
        
        self.assertIsInstance(response, str, "Ответ должен быть строкой")
        self.assertGreater(len(response), 0, "Ответ не должен быть пустым")
        
        print(f"✓ Получен ответ длиной {len(response)} символов")
        print(f"Ответ: {response[:100]}...")
    
    async def test_models_cache(self):
        """Тест на кэширование моделей"""
        if not self.api_key_available:
            self.skipTest("Пропуск теста, так как API ключ недоступен")
        
        print("Тест: Кэширование моделей")
        
        cache_file = self.client.models_cache_file
        # Удаляем кэш, если он существует
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        # Получаем модели (должен создаться кэш) - асинхронно с await
        models = await self.client.get_available_models(use_cache=False)
        
        # Проверяем, что кэш создан
        self.assertTrue(os.path.exists(cache_file), "Кэш-файл должен быть создан")
        
        # Загружаем кэш и проверяем его содержимое
        with open(cache_file, 'r') as f:
            cached_models = json.load(f)
        
        self.assertEqual(len(cached_models), len(models), "Количество моделей в кэше должно соответствовать полученному")
        print(f"✓ Кэш успешно создан с {len(cached_models)} моделями")
        
        # Проверяем, что при следующем вызове используется кэш - асинхронно с await
        cached_models_result = await self.client.get_available_models(use_cache=True)
        self.assertEqual(len(cached_models_result), len(models), "Количество моделей из кэша должно соответствовать оригинальному")
        print("✓ Кэш успешно используется при повторном запросе")


if __name__ == "__main__":
    unittest.main()
