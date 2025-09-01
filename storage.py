import json
from json import JSONDecodeError
from pathlib import Path

STORAGE_PATH = Path("flashcards.json")

def load_flashcards():
    if not STORAGE_PATH.exists():
        return []
    try:
        with STORAGE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (JSONDecodeError, ValueError):
        # corrupted or empty file -> return empty list
        return []

def save_flashcards(cards):
    existing = load_flashcards()
    if not isinstance(existing, list):
        existing = []
    existing.extend(cards)
    with STORAGE_PATH.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def clean_dataset():
    """Remove duplicate flashcards based on question similarity."""
    cards = load_flashcards()
    if not cards:
        print("No flashcards to clean")
        return
    
    seen_questions = set()
    unique_cards = []
    
    for card in cards:
        question = card.get('Question', '').strip().lower()
        if question and question not in seen_questions:
            seen_questions.add(question)
            unique_cards.append(card)
    
    # Save cleaned data
    with STORAGE_PATH.open("w", encoding="utf-8") as f:
        json.dump(unique_cards, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Cleaned dataset: {len(cards)} → {len(unique_cards)} unique flashcards")