import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Path Configuration
BASE_DIR = Path(__file__).parent
PERSONAS_PATH = BASE_DIR / "personas/all.json"
CONVERSATIONS_DIR = BASE_DIR / "data"
CONVERSATIONS_FILE = CONVERSATIONS_DIR / "conversations.json"

# Ensure directories exist
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

# Model Configuration
DEFAULT_MODEL = "gpt-4o"
AVAILABLE_MODELS = ["gpt-4o", "o1-mini", "o1-preview"]
