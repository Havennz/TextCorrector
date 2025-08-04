"""
Domain Services
===============
Core business logic and domain services
"""

import logging
import time
from typing import Protocol

from config import AI_PROMPTS
from .models import CorrectionRequest, CorrectionResult


class AIProvider(Protocol):
    """Protocol defining the interface for AI text generation providers."""
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate AI response for given prompt.
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If AI generation fails
        """
        ...


class TextCorrectionService:
    """
    Domain service responsible for text correction business logic.
    
    This service encapsulates the core business rules for text correction,
    including prompt building and result validation.
    """
    
    def __init__(self, ai_provider: AIProvider):
        """
        Initialize the text correction service.
        
        Args:
            ai_provider: AI provider implementation for text generation
        """
        self.ai_provider = ai_provider
        self.logger = logging.getLogger("TextCorrectionService")
    
    async def correct_text(self, request: CorrectionRequest) -> CorrectionResult:
        """
        Process a text correction request.
        
        Args:
            request: The correction request containing text and parameters
            
        Returns:
            CorrectionResult with the correction outcome
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not request.original_text.strip():
                return CorrectionResult(
                    original_text=request.original_text,
                    corrected_text="",
                    success=False,
                    error_message="Empty text provided",
                    processing_time=time.time() - start_time
                )
            
            # Build AI prompt
            prompt = self._build_correction_prompt(request.original_text, request.language)
            
            # Generate correction
            self.logger.info(f"Processing text correction for {len(request.original_text)} characters")
            corrected_text = await self.ai_provider.generate_response(prompt)
            
            # Validate result
            if not corrected_text.strip():
                return CorrectionResult(
                    original_text=request.original_text,
                    corrected_text="",
                    success=False,
                    error_message="AI returned empty response",
                    processing_time=time.time() - start_time
                )
            
            processing_time = time.time() - start_time
            self.logger.info(f"Text correction completed in {processing_time:.2f}s")
            
            return CorrectionResult(
                original_text=request.original_text,
                corrected_text=corrected_text.strip(),
                success=True,
                processing_time=processing_time
            )
            
        except Exception as e:
            error_msg = f"Text correction failed: {str(e)}"
            self.logger.error(error_msg)
            
            return CorrectionResult(
                original_text=request.original_text,
                corrected_text="",
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
    
    def _build_correction_prompt(self, text: str, language: str) -> str:
        """
        Build the AI prompt for text correction.
        
        Args:
            text: The text to be corrected
            language: The language for the prompt
            
        Returns:
            Complete prompt string for AI
        """
        prompt_template = AI_PROMPTS.get(language, AI_PROMPTS["Portuguese"])
        return f"{prompt_template}{text}"
    
    def validate_request(self, request: CorrectionRequest) -> tuple[bool, str]:
        """
        Validate a correction request.
        
        Args:
            request: The request to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not request.original_text:
            return False, "Text cannot be empty"
        
        if len(request.original_text.strip()) == 0:
            return False, "Text cannot be only whitespace"
        
        if len(request.original_text) > 10000:  # Reasonable limit
            return False, "Text is too long (max 10,000 characters)"
        
        if request.language not in AI_PROMPTS:
            return False, f"Unsupported language: {request.language}"
        
        return True, ""