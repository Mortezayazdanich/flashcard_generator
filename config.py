"""
Configuration Management for Flashcard Generator

Centralizes all configuration settings to replace hardcoded values throughout
the application and enable easy customization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path
import json
import os


@dataclass
class Config:
    """Central configuration for the flashcard generator."""
    
    # OCR Settings
    OCR_CONFIDENCE_THRESHOLD: float = 0.5
    OCR_DEFAULT_LANGUAGES: List[str] = field(default_factory=lambda: ['en'])
    
    # Text Processing Settings
    TARGET_WORDS_PER_CHUNK: int = 220
    CHUNK_OVERLAP_RATIO: float = 0.2
    MIN_SEGMENT_LENGTH: int = 50
    MAX_CHUNK_LENGTH: int = 2000
    
    # AI Generation Settings
    MAX_SUMMARY_TOKENS: int = 200
    MAX_QUESTION_TOKENS: int = 128
    MAX_ANSWER_TOKENS: int = 48
    DEFAULT_QUESTIONS_PER_SEGMENT: int = 3
    AI_MODEL_NAME: str = "google/flan-t5-base"
    
    # SpaCy Settings
    SPACY_MODEL_NAME: str = "en_core_web_sm"
    
    # File Paths
    FLASHCARDS_STORAGE: str = "flashcards.json"
    CONFIG_FILE: str = "flashcard_config.json"
    
    # Performance Settings
    ENABLE_MODEL_PRELOADING: bool = False
    ENABLE_CACHING: bool = True
    MAX_FILE_SIZE_MB: int = 100
    
    # Quality Filters
    MIN_ANSWER_WORDS: int = 2
    MIN_QUESTION_LENGTH: int = 5
    MAX_ANSWER_WORDS: int = 50
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def save_to_file(self, filepath: str = None) -> None:
        """Save current configuration to JSON file."""
        if filepath is None:
            filepath = self.CONFIG_FILE
            
        config_dict = {}
        for field_name, field_def in self.__dataclass_fields__.items():
            config_dict[field_name] = getattr(self, field_name)
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str = None) -> 'Config':
        """Load configuration from JSON file."""
        if filepath is None:
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
            print(f"Warning: Could not load config from {filepath}: {e}")
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
    print("⚠️ Configuration validation issues:")
    for issue in validation_issues:
        print(f"  - {issue}")


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
            print(f"Warning: Unknown configuration key: {key}")


def reset_config() -> None:
    """Reset configuration to defaults."""
    global config
    config = Config()
