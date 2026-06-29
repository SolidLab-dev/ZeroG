import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

# File Paths
ZEROG_DIR = os.path.expanduser("~/.zerog")
THREADS_DIR = os.path.join(ZEROG_DIR, "threads")
SETTINGS_FILE = os.path.join(ZEROG_DIR, "settings.json")

# Ensure required directories exist
os.makedirs(THREADS_DIR, exist_ok=True)
