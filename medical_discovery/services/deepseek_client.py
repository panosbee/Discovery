"""
DeepSeek AI Client
Wrapper for DeepSeek API interactions
"""
import httpx
from loguru import logger
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from medical_discovery.config import settings


class DeepSeekClient:
    """
    Client for DeepSeek AI API
    Handles all interactions with DeepSeek's language models
    """
    
    def __init__(self):
        """Initialize DeepSeek client"""
        self.api_key = settings.deepseek_api_key
        self.api_url = settings.deepseek_api_url
        self.model = settings.deepseek_model
        self.max_tokens = settings.deepseek_max_tokens
        self.temperature = settings.deepseek_temperature
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"DeepSeek client initialized with model: {self.model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to DeepSeek
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            response_format: Response format specification (e.g., {"type": "json_object"})
            
        Returns:
            API response dict
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            if response_format:
                payload["response_format"] = response_format
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.debug(f"DeepSeek API call successful, tokens used: {result.get('usage', {})}")
                
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"DeepSeek API HTTP error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: User prompt
            system_message: Optional system message to set context
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = await self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response["choices"][0]["message"]["content"]
    
    async def generate_json(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON from a prompt
        
        Args:
            prompt: User prompt requesting JSON output
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON dict
        """
        import json
        
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = await self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        content = response["choices"][0]["message"]["content"]
        
        # Safety check: if content is suspiciously long, it might be truncated/malformed
        if len(content) > 50000:
            logger.warning(f"DeepSeek returned very long response ({len(content)} chars). May be truncated.")
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Log first 1000 and last 500 chars to diagnose truncation issues
            logger.error(f"Failed to parse JSON response ({len(content)} chars)")
            logger.error(f"First 1000 chars: {content[:1000]}")
            logger.error(f"Last 500 chars: {content[-500:]}")
            logger.error(f"JSONDecodeError: {str(e)}")
            raise ValueError(f"Invalid JSON response from DeepSeek: {str(e)}")
    
    async def analyze_with_context(
        self,
        query: str,
        context: str,
        task_description: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Analyze a query with provided context
        
        Args:
            query: The question or task
            context: Context information
            task_description: Description of what the model should do
            temperature: Sampling temperature
            
        Returns:
            Analysis result
        """
        system_message = f"""You are an expert medical AI assistant specialized in {task_description}.
Analyze the provided information carefully and provide detailed, evidence-based responses."""
        
        prompt = f"""Context:
{context}

Query:
{query}

Please provide a comprehensive analysis based on the context provided."""
        
        return await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            temperature=temperature
        )


# Global DeepSeek client instance
deepseek_client = DeepSeekClient()
