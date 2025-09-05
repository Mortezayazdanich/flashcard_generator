"""
Custom Exceptions for Flashcard Generator

Provides specific exception types for different error scenarios to enable
better error handling and debugging throughout the application.
"""

from typing import Optional, Any


class FlashcardGeneratorError(Exception):
    """Base exception for flashcard generator."""
    
    def __init__(self, message: str, details: Optional[str] = None, original_error: Optional[Exception] = None):
        self.message = message
        self.details = details
        self.original_error = original_error
        
        full_message = message
        if details:
            full_message += f" Details: {details}"
        if original_error:
            full_message += f" Original error: {str(original_error)}"
            
        super().__init__(full_message)


class InputProcessingError(FlashcardGeneratorError):
    """Raised when input processing fails."""
    
    def __init__(self, file_path: str, reason: str, original_error: Optional[Exception] = None):
        message = f"Failed to process input file: {file_path}"
        super().__init__(message, reason, original_error)
        self.file_path = file_path


class ModelLoadingError(FlashcardGeneratorError):
    """Raised when model loading fails."""
    
    def __init__(self, model_name: str, model_type: str, original_error: Optional[Exception] = None):
        message = f"Failed to load {model_type} model: {model_name}"
        details = "Check your internet connection and available disk space"
        super().__init__(message, details, original_error)
        self.model_name = model_name
        self.model_type = model_type


class TextProcessingError(FlashcardGeneratorError):
    """Raised when text processing fails."""
    
    def __init__(self, operation: str, text_length: int, original_error: Optional[Exception] = None):
        message = f"Text processing failed during {operation}"
        details = f"Text length: {text_length} characters"
        super().__init__(message, details, original_error)
        self.operation = operation
        self.text_length = text_length


class AIGenerationError(FlashcardGeneratorError):
    """Raised when AI generation fails."""
    
    def __init__(self, generation_type: str, prompt_length: int, original_error: Optional[Exception] = None):
        message = f"AI generation failed for {generation_type}"
        details = f"Prompt length: {prompt_length} characters"
        super().__init__(message, details, original_error)
        self.generation_type = generation_type
        self.prompt_length = prompt_length


class StorageError(FlashcardGeneratorError):
    """Raised when storage operations fail."""
    
    def __init__(self, operation: str, file_path: str, original_error: Optional[Exception] = None):
        message = f"Storage operation '{operation}' failed"
        details = f"File: {file_path}"
        super().__init__(message, details, original_error)
        self.operation = operation
        self.file_path = file_path


class ConfigurationError(FlashcardGeneratorError):
    """Raised when configuration is invalid."""
    
    def __init__(self, parameter: str, value: Any, expected: str):
        message = f"Invalid configuration parameter: {parameter}"
        details = f"Value: {value}, Expected: {expected}"
        super().__init__(message, details)
        self.parameter = parameter
        self.value = value
        self.expected = expected


class FileTypeError(FlashcardGeneratorError):
    """Raised when file type is unsupported or cannot be determined."""
    
    def __init__(self, file_path: str, detected_type: str):
        message = f"Unsupported file type: {detected_type}"
        details = f"File: {file_path}"
        super().__init__(message, details)
        self.file_path = file_path
        self.detected_type = detected_type


class OCRError(FlashcardGeneratorError):
    """Raised when OCR processing fails."""
    
    def __init__(self, file_path: str, languages: list, original_error: Optional[Exception] = None):
        message = f"OCR processing failed"
        details = f"File: {file_path}, Languages: {languages}"
        super().__init__(message, details, original_error)
        self.file_path = file_path
        self.languages = languages
