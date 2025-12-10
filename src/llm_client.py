"""
llm_client.py
-------------
OpenAI API client wrapper.

This module provides a clean interface for interacting with the OpenAI
chat completion API. It centralizes API configuration and error handling,
making the rest of the codebase cleaner and easier to test.

Key responsibilities:
- API key management
- Request/response handling
- Error handling and retries
- Consistent interface for all LLM calls

Author: Srinath Begudem
"""

import os
from typing import Dict, List, Optional
import openai

from src.config import OPENAI_MODEL


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


def ensure_api_key() -> str:
    """
    Verify that the OpenAI API key is available.
    
    Checks the OPENAI_API_KEY environment variable and returns it if present.
    Raises a clear error message if the key is not configured.
    
    Returns:
        The API key string
        
    Raises:
        LLMClientError: If the API key is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise LLMClientError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Please set it using: export OPENAI_API_KEY='your-key-here'\n"
            "Or create a .env file with: OPENAI_API_KEY=your-key-here"
        )
    
    if api_key.startswith("sk-") is False:
        raise LLMClientError(
            "OPENAI_API_KEY does not appear to be a valid OpenAI key.\n"
            "OpenAI API keys typically start with 'sk-'"
        )
    
    return api_key


def call_chat_model(
    messages: List[Dict[str, str]],
    max_tokens: int = 1000,
    temperature: float = 0.7,
    model: str = OPENAI_MODEL
) -> str:
    """
    Make a chat completion request to the OpenAI API.
    
    This is the core function that all other modules use to interact
    with GPT-3.5-turbo. It handles API configuration and provides
    a clean interface for message-based interactions.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
                  Roles can be 'system', 'user', or 'assistant'
        max_tokens: Maximum tokens in the response
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        model: Model identifier (locked to gpt-3.5-turbo per requirements)
        
    Returns:
        The assistant's response text
        
    Raises:
        LLMClientError: If the API call fails
        
    Example:
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant."},
        ...     {"role": "user", "content": "Hello!"}
        ... ]
        >>> response = call_chat_model(messages, max_tokens=100)
        >>> print(response)
        'Hello! How can I help you today?'
    """
    # Ensure API key is available
    api_key = ensure_api_key()
    openai.api_key = api_key
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False
        )
        
        # Extract the response content
        return response.choices[0].message["content"]  # type: ignore
        
    except openai.error.AuthenticationError as e:
        raise LLMClientError(
            f"OpenAI API authentication failed. Please check your API key.\n"
            f"Error: {e}"
        )
    except openai.error.RateLimitError as e:
        raise LLMClientError(
            f"OpenAI API rate limit exceeded. Please wait and try again.\n"
            f"Error: {e}"
        )
    except openai.error.APIError as e:
        raise LLMClientError(
            f"OpenAI API error occurred.\n"
            f"Error: {e}"
        )
    except Exception as e:
        raise LLMClientError(
            f"Unexpected error during API call.\n"
            f"Error type: {type(e).__name__}\n"
            f"Error: {e}"
        )


def call_model(prompt: str, max_tokens: int = 3000, temperature: float = 0.1) -> str:
    """
    Simple wrapper matching the original skeleton interface.
    
    This function provides backwards compatibility with the original
    main.py interface. It converts a simple prompt string into the
    message format expected by call_chat_model.
    
    Args:
        prompt: The user prompt as a simple string
        max_tokens: Maximum response tokens
        temperature: Sampling temperature
        
    Returns:
        The model's response text
        
    Note:
        For new code, prefer call_chat_model which supports system prompts
        and multi-turn conversations.
    """
    messages = [{"role": "user", "content": prompt}]
    return call_chat_model(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
