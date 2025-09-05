import json
import logging
from json import JSONDecodeError
from pathlib import Path
from typing import List, Dict, Set, Optional, Any
from ..config.settings import get_config
from ..utils.exceptions import StorageError


class FlashcardStorage:
    """Optimized flashcard storage with caching and efficient operations."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.config = get_config()
        self.storage_path = Path(storage_path or self.config.FLASHCARDS_STORAGE)
        self.logger = logging.getLogger(__name__)
        self._cache: Optional[List[Dict[str, str]]] = None
        self._cache_dirty = False
    
    def _load_from_disk(self) -> List[Dict[str, str]]:
        """Load flashcards from disk."""
        if not self.storage_path.exists():
            return []
        
        try:
            with self.storage_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Corrupted storage file, returning empty list: {e}")
            return []
        except Exception as e:
            raise StorageError("load", str(self.storage_path), e)
    
    def _save_to_disk(self, cards: List[Dict[str, str]]) -> None:
        """Save flashcards to disk."""
        try:
            # Create backup if file exists
            if self.storage_path.exists():
                backup_path = self.storage_path.with_suffix('.json.backup')
                self.storage_path.rename(backup_path)
            
            with self.storage_path.open("w", encoding="utf-8") as f:
                json.dump(cards, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise StorageError("save", str(self.storage_path), e)
    
    def load_flashcards(self) -> List[Dict[str, str]]:
        """Load flashcards with caching."""
        if self._cache is None or self._cache_dirty:
            self._cache = self._load_from_disk()
            self._cache_dirty = False
        return self._cache.copy()  # Return copy to prevent external modification
    
    def save_flashcards(self, cards: List[Dict[str, str]], append: bool = True) -> None:
        """Save flashcards efficiently."""
        if not cards:
            return
        
        if append:
            existing = self._load_from_disk()  # Load fresh from disk for append
            existing.extend(cards)
            self._cache = existing
        else:
            self._cache = cards.copy()
        
        self._save_to_disk(self._cache)
        self._cache_dirty = False
    
    def clean_dataset(self) -> int:
        """Remove duplicate flashcards and return number of removed duplicates."""
        cards = self._load_from_disk()  # Load fresh from disk
        if not cards:
            self.logger.info("No flashcards to clean")
            return 0
        
        # Use more efficient deduplication
        seen_questions: Set[str] = set()
        unique_cards: List[Dict[str, str]] = []
        
        for card in cards:
            question = card.get('Question', '').strip().lower()
            if question and question not in seen_questions:
                seen_questions.add(question)
                unique_cards.append(card)
        
        # Only save if there were duplicates
        duplicates_removed = len(cards) - len(unique_cards)
        if duplicates_removed > 0:
            self._cache = unique_cards
            self._save_to_disk(unique_cards)
            self._cache_dirty = False
            
            self.logger.info(f"Cleaned dataset: {len(cards)} → {len(unique_cards)} unique flashcards")
        
        return duplicates_removed
    
    def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self._cache = None
        self._cache_dirty = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        cards = self.load_flashcards()
        return {
            'total_cards': len(cards),
            'file_size_bytes': self.storage_path.stat().st_size if self.storage_path.exists() else 0,
            'cache_loaded': self._cache is not None,
            'cache_dirty': self._cache_dirty
        }


# Global storage instance
_storage = FlashcardStorage()


# Backward compatible functions
def load_flashcards() -> List[Dict[str, str]]:
    """Load flashcards using the global storage instance."""
    return _storage.load_flashcards()


def save_flashcards(cards: List[Dict[str, str]]) -> None:
    """Save flashcards using the global storage instance."""
    _storage.save_flashcards(cards)


def clean_dataset() -> int:
    """Clean dataset using the global storage instance."""
    duplicates_removed = _storage.clean_dataset()
    if duplicates_removed > 0:
        print(f"\n✅ Cleaned dataset: removed {duplicates_removed} duplicates")
    return duplicates_removed
