import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# App paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_FILE = DATA_DIR / "analyzed_feedbacks.json"

# LLM Config
LLM_API_KEY = os.getenv("LLM_API_KEY")

def init_app():
    """Ensure necessary directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
