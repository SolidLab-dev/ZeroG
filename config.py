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
LOGS_DIR = os.path.join(ZEROG_DIR, "logs")

# Ensure required directories exist
os.makedirs(THREADS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

import logging
from logging.handlers import RotatingFileHandler

# Logger Setup
logger = logging.getLogger("ZeroG")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# Console Handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File Handler (Max 5MB per file, keep 3 backups)
log_file = os.path.join(LOGS_DIR, "zerog.log")
fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
fh.setFormatter(formatter)
logger.addHandler(fh)
