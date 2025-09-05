"""
Unified Model Manager for Flashcard Generator

Centralizes model loading and management to optimize memory usage and startup time.
Implements singleton pattern with lazy loading for efficient resource management.
"""

import logging
import spacy
import easyocr
from transformers import pipeline
from typing import Dict, List, Optional, Any
from threading import Lock


class ModelManager:
    """Singleton model manager for centralized model loading and caching."""
    
    _instance: Optional['ModelManager'] = None
    _lock = Lock()
    
    def __init__(self):
        if ModelManager._instance is not None:
            raise RuntimeError("ModelManager is a singleton. Use get_instance() instead.")
        
        self._models: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    @classmethod
    def get_instance(cls) -> 'ModelManager':
        """Get the singleton instance of ModelManager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def get_nlp_model(self, model_name: str = "en_core_web_sm") -> spacy.Language:  # type: ignore
        """Get spaCy NLP model with lazy loading."""
        cache_key = f"spacy_{model_name}"
        
        if cache_key not in self._models:
            self.logger.info(f"Loading spaCy model: {model_name}")
            try:
                self._models[cache_key] = spacy.load(model_name)
                self.logger.info(f"✅ Successfully loaded spaCy model: {model_name}")
            except Exception as e:
                self.logger.error(f"Failed to load spaCy model {model_name}: {e}")
                raise RuntimeError(f"Could not load spaCy model '{model_name}'. "
                                 f"Install it with: python -m spacy download {model_name}")
        
        return self._models[cache_key]
    
    def get_ai_generator(self, model_name: str = "google/flan-t5-base") -> Any:
        """Get AI text generation model with lazy loading."""
        cache_key = f"generator_{model_name.replace('/', '_')}"
        
        if cache_key not in self._models:
            self.logger.info(f"Loading AI generator model: {model_name}")
            try:
                self._models[cache_key] = pipeline("text2text-generation", model=model_name)
                self.logger.info(f"✅ Successfully loaded AI generator: {model_name}")
            except Exception as e:
                self.logger.error(f"Failed to load AI generator {model_name}: {e}")
                raise RuntimeError(f"Could not load AI model '{model_name}'. "
                                 f"Check your internet connection and available disk space.")
        
        return self._models[cache_key]
    
    def get_ocr_reader(self, languages: List[str] = ['en']) -> easyocr.Reader:
        """Get EasyOCR reader with lazy loading and language caching."""
        cache_key = f"ocr_{'_'.join(sorted(languages))}"
        
        if cache_key not in self._models:
            self.logger.info(f"Loading EasyOCR reader for languages: {languages}")
            try:
                self._models[cache_key] = easyocr.Reader(languages)
                self.logger.info(f"✅ Successfully loaded EasyOCR for: {languages}")
            except Exception as e:
                self.logger.error(f"Failed to load EasyOCR for {languages}: {e}")
                raise RuntimeError(f"Could not load EasyOCR for languages '{languages}'. "
                                 f"Check your internet connection and available disk space.")
        
        return self._models[cache_key]
    
    def preload_models(self, include_ocr: bool = False, ocr_languages: List[str] = ['en']) -> None:
        """Preload all models for faster runtime performance."""
        self.logger.info("Preloading models for optimal performance...")
        
        try:
            # Load NLP model
            self.get_nlp_model()
            
            # Load AI generator
            self.get_ai_generator()
            
            # Optionally load OCR (can be memory intensive)
            if include_ocr:
                self.get_ocr_reader(ocr_languages)
                
            self.logger.info("✅ All models preloaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Model preloading failed: {e}")
            raise
    
    def get_memory_usage(self) -> Dict[str, str]:
        """Get approximate memory usage of loaded models."""
        import sys
        
        usage = {}
        for model_name, model in self._models.items():
            # Rough size estimation
            size_bytes = sys.getsizeof(model)
            if hasattr(model, 'model') and hasattr(model.model, 'num_parameters'):
                # For transformer models, estimate based on parameters
                params = model.model.num_parameters()
                size_bytes = params * 4  # Assume 4 bytes per parameter (float32)
            
            size_mb = size_bytes / (1024 * 1024)
            usage[model_name] = f"{size_mb:.1f} MB"
        
        return usage
    
    def clear_cache(self, model_type: Optional[str] = None) -> None:
        """Clear model cache to free memory."""
        if model_type:
            # Clear specific model type
            keys_to_remove = [k for k in self._models.keys() if k.startswith(model_type)]
            for key in keys_to_remove:
                del self._models[key]
                self.logger.info(f"Cleared {key} from cache")
        else:
            # Clear all models
            self._models.clear()
            self.logger.info("Cleared all models from cache")


# Convenience functions for backward compatibility
def get_nlp_model() -> spacy.Language:  # type: ignore
    """Get spaCy model via ModelManager."""
    return ModelManager.get_instance().get_nlp_model()

def get_ai_generator() -> Any:
    """Get AI generator via ModelManager."""
    return ModelManager.get_instance().get_ai_generator()

def get_ocr_reader(languages: List[str] = ['en']) -> easyocr.Reader:
    """Get OCR reader via ModelManager."""
    return ModelManager.get_instance().get_ocr_reader(languages)
