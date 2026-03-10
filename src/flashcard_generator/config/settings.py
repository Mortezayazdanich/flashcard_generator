"""
Configuration Management for Flashcard Generator

Centralizes all configuration settings to replace hardcoded values throughout
the application and enable easy customization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import os
import logging


def _getenv_str(key: str, default: str = '') -> str:
    """Get an environment variable as a string."""
    return os.getenv(key, default)

def _getenv_int(key: str, default: int = 0) -> int:
    """Get an environment variable as an integer."""
    return int(os.getenv(key, default))

def _getenv_float(key: str, default: float = 0.0) -> float:
    """Get an environment variable as a float."""
    return float(os.getenv(key, default))

def _getenv_bool(key: str, default: bool = False) -> bool:
    """Get an environment variable as a boolean."""
    return os.getenv(key, str(default)).lower() in ('true', '1', 'yes', 'on')

def _getenv_list(key: str, default: str = '') -> List[str]:
    """Get an environment variable as a list, split by comma."""
    value = os.getenv(key, default)
    if not value:
        return []
    return [item.strip() for item in value.split(',')]


logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Central configuration for the flashcard generator."""

    # General Settings
    DEBUG: bool = _getenv_bool('DEBUG', False)

    # AI Settings
    MODEL_NAME = _getenv_str("MODEL_NAME", "google/flan-t5-base")
    NUM_QS = _getenv_int("NUM_QS", 3)
    SEGMENT_WORDS = _getenv_int("SEGMENT_WORDS", 220)
    SEGMENT_OVERLAP = _getenv_float("SEGMENT_OVERLAP", 0.2)
    OCR_LANGS = _getenv_list("OCR_LANGS", "en")
    STORAGE_PATH = Path(_getenv_str("STORAGE_PATH", "flashcards.json"))
    SPACY_MODEL = _getenv_str("SPACY_MODEL", "en_core_web_sm")

    # OCR Settings
    OCR_CONFIDENCE_THRESHOLD: float = _getenv_float("OCR_CONFIDENCE_THRESHOLD", 0.5)
    OCR_DEFAULT_LANGUAGES: List[str] = field(default_factory=lambda: ['en'])
    
    # Text Processing Settings
    TARGET_WORDS_PER_CHUNK: int = _getenv_int("TARGET_WORDS_PER_CHUNK", 220)    
    CHUNK_OVERLAP_RATIO: float = _getenv_float("CHUNK_OVERLAP_RATIO", 0.2)
    MIN_SEGMENT_LENGTH: int = _getenv_int("MIN_SEGMENT_LENGTH", 50)
    MAX_CHUNK_LENGTH: int = _getenv_int("MAX_CHUNK_LENGTH", 2000)

    # AI Generation Settings
    MAX_SUMMARY_TOKENS: int = _getenv_int("MAX_SUMMARY_TOKENS", 200)
    MAX_QUESTION_TOKENS: int = _getenv_int("MAX_QUESTION_TOKENS", 128)
    MAX_ANSWER_TOKENS: int = _getenv_int("MAX_ANSWER_TOKENS", 48)
    DEFAULT_QUESTIONS_PER_SEGMENT: int = _getenv_int("DEFAULT_QUESTIONS_PER_SEGMENT", 3)
    AI_MODEL_NAME: str = _getenv_str("AI_MODEL_NAME", "google/flan-t5-base")
    
    # SpaCy Settings
    SPACY_MODEL_NAME: str = _getenv_str("SPACY_MODEL_NAME", "en_core_web_sm")
    
    # File Paths
    FLASHCARDS_STORAGE: str = _getenv_str("FLASHCARDS_STORAGE", "data/flashcards.json")
    CONFIG_FILE: str = _getenv_str("CONFIG_FILE", "flashcard_config.json")
    
    # Performance Settings
    ENABLE_MODEL_PRELOADING: bool = _getenv_bool("ENABLE_MODEL_PRELOADING", False)
    ENABLE_CACHING: bool = _getenv_bool("ENABLE_CACHING", True)
    MAX_FILE_SIZE_MB: int = _getenv_int("MAX_FILE_SIZE_MB", 100)
    
    # Quality Filters
    MIN_ANSWER_WORDS: int = _getenv_int("MIN_ANSWER_WORDS", 2)
    MIN_QUESTION_LENGTH: int = _getenv_int("MIN_QUESTION_LENGTH", 5)
    MAX_ANSWER_WORDS: int = _getenv_int("MAX_ANSWER_WORDS", 50)
    
    # Logging Settings
    LOG_LEVEL: str = _getenv_str("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = _getenv_str("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def save_to_file(self, filepath: str = '') -> None:
        """Save current configuration to JSON file."""
        if filepath == '':
            filepath = self.CONFIG_FILE
            
        config_dict = {}
        for field_name, field_def in self.__dataclass_fields__.items():
            config_dict[field_name] = getattr(self, field_name)
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str = '') -> 'Config':
        """Load configuration from JSON file."""
        if filepath == '':
            filepath = cls.__dataclass_fields__['CONFIG_FILE'].default
            
        if not os.path.exists(filepath):
            # Return default config if file doesn't exist
            return cls()
        
        try:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            
            # Create config instance with loaded values
            return cls(**config_dict)
            
        except (json.JSONDecodeError, TypeError) as e:
            # Return default config if loading fails
            logger.warning(f"Could not load config from {filepath}: {e}")
            return cls()
    
    def update_from_env(self) -> None:
        """Update configuration from environment variables."""
        env_mappings = {
            'FLASHCARD_AI_MODEL': 'AI_MODEL_NAME',
            'FLASHCARD_SPACY_MODEL': 'SPACY_MODEL_NAME',
            'FLASHCARD_LOG_LEVEL': 'LOG_LEVEL',
            'FLASHCARD_MAX_FILE_SIZE': 'MAX_FILE_SIZE_MB',
            'FLASHCARD_OCR_THRESHOLD': 'OCR_CONFIDENCE_THRESHOLD',
            'FLASHCARD_TARGET_WORDS': 'TARGET_WORDS_PER_CHUNK',
        }
        
        for env_var, config_attr in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Type conversion based on current attribute type
                current_value = getattr(self, config_attr)
                if isinstance(current_value, int):
                    value = int(value)
                elif isinstance(current_value, float):
                    value = float(value)
                elif isinstance(current_value, bool):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                setattr(self, config_attr, value)
    
    def validate(self) -> List[str]:
        """Validate configuration values and return list of issues."""
        issues = []
        
        # Validate ranges
        if not 0.0 <= self.OCR_CONFIDENCE_THRESHOLD <= 1.0:
            issues.append("OCR_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        
        if not 0.0 <= self.CHUNK_OVERLAP_RATIO <= 1.0:
            issues.append("CHUNK_OVERLAP_RATIO must be between 0.0 and 1.0")
        
        if self.TARGET_WORDS_PER_CHUNK <= 0:
            issues.append("TARGET_WORDS_PER_CHUNK must be positive")
        
        if self.MIN_SEGMENT_LENGTH <= 0:
            issues.append("MIN_SEGMENT_LENGTH must be positive")
        
        if self.MAX_FILE_SIZE_MB <= 0:
            issues.append("MAX_FILE_SIZE_MB must be positive")
        
        # Validate file paths
        storage_dir = Path(self.FLASHCARDS_STORAGE).parent
        if storage_dir != Path('.') and not storage_dir.exists():
            issues.append(f"Storage directory does not exist: {storage_dir}")
        
        return issues


# Global configuration instance
config = Config()

# Load from file and environment on import
config = Config.load_from_file()
config.update_from_env()

# Validate configuration
validation_issues = config.validate()
if validation_issues:
    logger.warning("⚠️ Configuration validation issues:")
    for issue in validation_issues:
        logger.warning(f"  - {issue}")


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def update_config(**kwargs) -> None:
    """Update configuration values at runtime."""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key.upper()):
            setattr(config, key.upper(), value)
        else:
            logger.warning(f"Unknown configuration key: {key}")


def reset_config() -> None:
    """Reset configuration to defaults."""
    global config
    config = Config()
