import json
from src.config import STORAGE_FILE, init_app

def load_data():
    """Load analyzed feedbacks from JSON storage."""
    init_app()
    if not STORAGE_FILE.exists():
        return []
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def save_data(data):
    """Save analyzed feedbacks to JSON storage."""
    init_app()
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")
