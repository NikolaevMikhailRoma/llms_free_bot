#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""OpenRouter API client for accessing language models asynchronously."""

import os
import json
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenRouterClient:
    """Asynchronous client for interacting with OpenRouter API.
    
    Provides methods to fetch available models and generate responses from
    language models through OpenRouter's unified API.
    """
    
    def __init__(self):
        """Initialize the OpenRouter client with API key and configuration."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://telegram-bot-openrouter.example.com",
        }
        self.models_cache_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'models_cache.json')
        self._session = None  # Session will be created when first needed
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get existing HTTP session or create a new one."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
        
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_available_models(self, use_cache=True) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter.
        
        Args:
            use_cache: Whether to use cached models data if available
            
        Returns:
            List of model information dictionaries
        """
        # Check if cache exists and can be used
        if use_cache and os.path.exists(self.models_cache_file):
            try:
                with open(self.models_cache_file, 'r') as f:
                    models_data = json.load(f)
                    if models_data:
                        return models_data
            except Exception as e:
                print(f"Error reading cache: {e}")
        
        # If no cache or can't use it, fetch from API
        session = await self._get_session()
        async with session.get(
            f"{self.base_url}/models",
            headers=self.headers
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Error fetching models: {error_text}")
            
            # Get model data
            json_data = await response.json()
            models_data = json_data.get('data', [])
        
        # Save to cache
        await self._save_models_cache(models_data)
        
        await response.release()
        
        return models_data
    
    async def _save_models_cache(self, models_data):
        """Save models data to cache file asynchronously."""
        # Create cache directory if it doesn't exist
        os.makedirs(os.path.dirname(self.models_cache_file), exist_ok=True)
        
        try:
            # Run file saving in a separate task to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,  # use default executor
                self._save_models_cache_sync, models_data
            )
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _save_models_cache_sync(self, models_data):
        """Synchronous version of cache saving (runs in executor)."""
        with open(self.models_cache_file, 'w') as f:
            json.dump(models_data, f, indent=2)
    
    async def get_free_models(self, limit=None) -> List[Dict[str, Any]]:
        """Get only truly free models from OpenRouter.
        
        Args:
            limit: Maximum number of models to return, None for all models
            
        Returns:
            List of completely free model information dictionaries, sorted by preference
        """
        models_data = await self.get_available_models()
        
        # Filter only completely free models
        free_models = []
        for model in models_data:
            # Check if name or ID contains "free"
            is_free_in_name = "free" in model.get("id", "").lower() or "free" in model.get("name", "").lower()
            
            # Only include models that are explicitly marked as free
            if is_free_in_name:
                free_models.append({
                    "id": model.get("id"),
                    "name": model.get("name"),
                    "description": model.get("description", ""),
                    "context_length": model.get("context_length", 4096),
                    "is_free": True
                })
        
        # Sort by context length (larger first)
        free_models.sort(key=lambda x: -x["context_length"])
        
        # Return models with optional limit
        if limit is not None and limit > 0:
            return free_models[:limit]
        return free_models
    
    async def generate_response(self, model_id: str, prompt: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response from a specified model.
        
        Args:
            model_id: ID of the model to use
            prompt: User's query text
            chat_history: Previous messages in the conversation
            
        Returns:
            Generated response text from the language model
        """
        if chat_history is None:
            chat_history = []
        
        # Prepare messages for API
        messages = []
        
        # Add chat history
        for msg in chat_history:
            messages.append(msg)
            
        # Add current request
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model_id,
            "messages": messages
        }
        
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=60)  # Extended timeout for response generation
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Error generating response: {error_text}")
            
            response_data = await response.json()
            result = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        await response.release()
        
        return result
