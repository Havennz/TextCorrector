"""
AI Providers
============
Implementations of AI service providers
"""

import asyncio
import logging
from typing import Optional

import google.generativeai as genai


class GeminiAIProvider:
    """
    Google Gemini AI provider implementation - VERSÃO CORRIGIDA.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """Initialize Gemini AI provider."""
        self.api_key = api_key
        self.model_name = model_name
        self.model: Optional[genai.GenerativeModel] = None
        self.logger = logging.getLogger("GeminiAIProvider")
        
        self._configure()
    
    def _configure(self) -> None:
        """Configure the Gemini AI model."""
        try:
            if not self.api_key:
                raise ValueError("API key is required")
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            
            self.logger.info(f"Gemini AI configured successfully with model: {self.model_name}")
            
        except Exception as e:
            error_msg = f"Failed to configure Gemini AI: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate AI response for the given prompt - VERSÃO CORRIGIDA.
        
        Args:
            prompt: The prompt to send to Gemini AI
            
        Returns:
            Generated response text (properly cleaned)
            
        Raises:
            Exception: If AI generation fails
        """
        if not self.model:
            raise Exception("Gemini AI model not configured")
        
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            self.logger.debug(f"Sending prompt to Gemini AI (length: {len(prompt)})")
            
            # Use asyncio.to_thread to run the synchronous AI call in a thread pool
            response = await asyncio.to_thread(self._generate_content_sync, prompt)
            
            if not response or not hasattr(response, "text") or not response.text:
                raise Exception("Empty or invalid response from Gemini AI")
            
            # CORREÇÃO PRINCIPAL: Limpeza robusta da resposta
            result = self._clean_response(response.text)
            
            self.logger.debug(f"Received response from Gemini AI (length: {len(result)})")
            
            return result
            
        except Exception as e:
            error_msg = f"Gemini AI generation failed: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def _clean_response(self, raw_response: str) -> str:
        """
        Clean and normalize the AI response.
        
        Args:
            raw_response: Raw response from Gemini
            
        Returns:
            Cleaned response string
        """
        try:
            # Convert to string if needed
            if not isinstance(raw_response, str):
                raw_response = str(raw_response)
            
            # Remove B' prefix and ' suffix if present (bytes representation)
            if raw_response.startswith("B'") or raw_response.startswith('B"'):
                raw_response = raw_response[2:]
            
            if raw_response.endswith("'") or raw_response.endswith('"'):
                raw_response = raw_response[:-1]
            
            # Remove common prefixes that might appear
            prefixes_to_remove = [
                "b'", 'b"',  # bytes prefix
                "r'", 'r"',  # raw string prefix
                "u'", 'u"',  # unicode prefix
            ]
            
            for prefix in prefixes_to_remove:
                if raw_response.lower().startswith(prefix):
                    raw_response = raw_response[len(prefix):]
                    break
            
            # Remove trailing quotes
            suffixes_to_remove = ["'", '"']
            for suffix in suffixes_to_remove:
                if raw_response.endswith(suffix):
                    raw_response = raw_response[:-len(suffix)]
                    break
            
            # Decode if it's still bytes-like
            if raw_response.startswith('\\x') or '\\n' in raw_response:
                try:
                    # Try to decode escape sequences
                    raw_response = raw_response.encode().decode('unicode_escape')
                except:
                    pass  # If decoding fails, keep original
            
            # Final cleanup
            result = raw_response.strip()
            
            # Log the cleaning process for debugging
            if result != raw_response.strip():
                self.logger.debug(f"Response cleaned: '{raw_response.strip()}' -> '{result}'")
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error cleaning response, returning raw: {e}")
            return str(raw_response).strip()
    
    def _generate_content_sync(self, prompt: str):
        """
        Synchronous wrapper for Gemini's generate_content method.
        
        Args:
            prompt: The prompt to generate content for
            
        Returns:
            Gemini AI response object
        """
        return self.model.generate_content(prompt)
    
    async def health_check(self) -> bool:
        """Perform a health check on the AI provider."""
        try:
            test_prompt = "Test prompt for health check. Please respond with 'OK'."
            response = await self.generate_response(test_prompt)
            
            # Simple check if we got any meaningful response
            return bool(response and len(response.strip()) > 0)
            
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False
    
    def get_model_info(self) -> dict:
        """Get information about the current AI model."""
        return {
            "provider": "Google Gemini",
            "model_name": self.model_name,
            "api_configured": self.model is not None,
            "api_key_provided": bool(self.api_key)
        }


class MockAIProvider:
    """
    Mock AI provider for testing purposes.
    
    This provider can be used during development and testing
    to avoid API calls and costs.
    """
    
    def __init__(self, response_delay: float = 0.5):
        """
        Initialize mock AI provider.
        
        Args:
            response_delay: Artificial delay to simulate AI processing time
        """
        self.response_delay = response_delay
        self.logger = logging.getLogger("MockAIProvider")
        self.call_count = 0
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate mock AI response.
        
        Args:
            prompt: The input prompt (analyzed for mock response)
            
        Returns:
            Mock corrected text
        """
        self.call_count += 1
        
        # Simulate processing time
        await asyncio.sleep(self.response_delay)
        
        # Extract text from prompt (assuming it ends with the actual text)
        lines = prompt.split('\n')
        text_to_correct = ""
        
        # Find the actual text (usually after the prompt instructions)
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(("Corrija", "Fix", "Text:")):
                text_to_correct = '\n'.join(lines[i:])
                break
        
        if not text_to_correct:
            text_to_correct = "Mock corrected text."
        
        # Simple mock correction: add punctuation if missing
        corrected = text_to_correct.strip()
        if corrected and not corrected.endswith(('.', '!', '?')):
            corrected += '.'
        
        self.logger.info(f"Mock AI response generated (call #{self.call_count})")
        return corrected
    
    async def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True
    
    def get_model_info(self) -> dict:
        """Get mock model information."""
        return {
            "provider": "Mock AI Provider",
            "model_name": "mock-model-v1",
            "api_configured": True,
            "api_key_provided": True,
            "call_count": self.call_count
        }