#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import json
from dotenv import load_dotenv
import asyncio

# Add the project root directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import OpenRouter client
from src.api.openrouter_api import OpenRouterClient

# Load environment variables
load_dotenv()

# Use IsolatedAsyncioTestCase for asynchronous tests
class TestOpenRouterAPI(unittest.IsolatedAsyncioTestCase):
    """Tests for OpenRouter API"""
    
    def setUp(self):
        """Set up environment for tests"""
        self.client = OpenRouterClient()
        # Check if API key is available
        self.api_key_available = bool(os.getenv("OPENROUTER_API_KEY"))
        
        # Display documentation information
        self.print_documentation_info()
    
    async def asyncTearDown(self):
        """Close client session after each test"""
        if self.client:
            await self.client.close()

    def print_documentation_info(self):
        """Displays information about documentation access"""
        print("\n=== Documentation Check ===")
        print("OpenRouter API Documentation [@docs:openrouter-api]: https://openrouter.ai/docs")
        print("Telegram Bot API Documentation [@docs:telegram-bot-api]: https://core.telegram.org/bots/api")
        print("================================\n")
    
    async def test_api_key_loaded(self):
        """Test for loading API key from .env file"""
        print("Test: Checking for OpenRouter API key presence")
        self.assertTrue(self.api_key_available, "API key should be available from .env file")
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.assertIsNotNone(api_key, "API key should be loaded")
        self.assertTrue(api_key.startswith("sk-or-"), "API key should have the format 'sk-or-*'")
        print(f"✓ OpenRouter API key successfully loaded: {api_key[:10]}...")
    
    async def test_get_available_models(self):
        """Test for getting available models"""
        if not self.api_key_available:
            self.skipTest("Skipping test as API key is unavailable")
        
        print("Test: Getting a list of all models")
        # Using await instead of asyncio.run()
        models = await self.client.get_available_models(use_cache=False)
        self.assertIsInstance(models, list, "get_available_models should return a list")
        self.assertGreater(len(models), 0, "There should be at least one model")
        
        # Check the model data format
        model = models[0]
        required_fields = ["id", "name"]
        for field in required_fields:
            self.assertIn(field, model, f"Model should contain the field '{field}'")
        
        print(f"✓ Received {len(models)} models")
        print(f"Sample model: {model['name']} ({model['id']})")
    
    async def test_get_free_models(self):
        """Test for getting free models"""
        if not self.api_key_available:
            self.skipTest("Skipping test as API key is unavailable")
        
        print("Test: Getting list of free models")
        # Using await instead of asyncio.run()
        free_models = await self.client.get_free_models(limit=10)
        self.assertIsInstance(free_models, list, "get_free_models should return a list")
        
        print(f"✓ Received {len(free_models)} free models")
        
        # Check that the list contains models with "free" in their name
        free_in_name_count = sum(1 for model in free_models if model.get("is_free", False))
        print(f"✓ Models with 'free' in the name: {free_in_name_count}")
        
        # Display list of free models
        print("\nList of free models:")
        for i, model in enumerate(free_models, 1):
            is_free = "🆓" if model.get("is_free", False) else "  "
            print(f"{i}. {is_free} {model['name']} ({model['id']})")
    
    async def test_generate_response(self):
        """Test for generating response from a model"""
        if not self.api_key_available:
            self.skipTest("Skipping test as API key is unavailable")
        
        print("Test: Generating a response from a model")
        
        # Use a known working model from OpenRouter
        # Rather than trying the first free model which might not be stable
        model_id = "meta-llama/llama-4-scout:free"  # This model is known to be reliable
        model_name = "Meta Llama 4 Scout (free)"
        
        print(f"✓ Using model: {model_name} ({model_id})")
        
        # Generate response (asynchronously with await)
        prompt = "Tell me about yourself in one sentence as an AI assistant."
        print(f"✓ Sending request: '{prompt}'")
        
        try:
            response = await self.client.generate_response(model_id, prompt)
        except Exception as e:
            # If the test model fails for some reason, try a fallback
            print(f"⚠️ First model failed: {e}")
            print("⚠️ Trying fallback model...")
            fallback_model_id = "deepseek/deepseek-v3-base:free"
            response = await self.client.generate_response(fallback_model_id, prompt)
        
        self.assertIsInstance(response, str, "Response should be a string")
        self.assertGreater(len(response), 0, "Response should not be empty")
        
        print(f"✓ Received response of {len(response)} characters")
        print(f"Response: {response[:100]}...")
    
    async def test_models_cache(self):
        """Test for model caching"""
        if not self.api_key_available:
            self.skipTest("Skipping test as API key is unavailable")
        
        print("Test: Model caching")
        
        cache_file = self.client.models_cache_file
        # Delete cache if it exists
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        # Get models (should create cache) - asynchronously with await
        models = await self.client.get_available_models(use_cache=False)
        
        # Check that the cache was created
        self.assertTrue(os.path.exists(cache_file), "Cache file should be created")
        
        # Load cache and check its contents
        with open(cache_file, 'r') as f:
            cached_models = json.load(f)
        
        self.assertEqual(len(cached_models), len(models), "Number of models in cache should match the received ones")
        print(f"✓ Cache successfully created with {len(cached_models)} models")
        
        # Check that cache is used on next call - asynchronously with await
        cached_models_result = await self.client.get_available_models(use_cache=True)
        self.assertEqual(len(cached_models_result), len(models), "Number of models from cache should match the original")
        print("✓ Cache successfully used for repeat requests")


if __name__ == "__main__":
    unittest.main()
