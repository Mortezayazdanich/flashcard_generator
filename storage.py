import json
from json import JSONDecodeError
from pathlib import Path
import pandas as pd

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
    try:
        # 1. Read the JSON file into a pandas DataFrame
        df = pd.read_json(STORAGE_PATH)

        # 2. Drop duplicate rows. It's that simple!
        # To drop based on a specific column, use: df.drop_duplicates(subset=['id'], keep='first')
        df_unique = df.drop_duplicates(subset=['Question'], keep='first')

        # 3. Write the cleaned DataFrame back to a JSON file
        # orient='records' creates a list of dictionaries, like the original format.
        df_unique.to_json(STORAGE_PATH, orient='records', indent=4)

        print(f"✅ Pandas cleaned the file and saved it to {STORAGE_PATH}")
        print(f"Original items: {len(df)}, Unique items: {len(df_unique)}")

    except FileNotFoundError:
        print(f"Error: File not found at {STORAGE_PATH}")
    except Exception as e:
        print(f"An error occurred: {e}")