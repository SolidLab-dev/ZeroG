import os
from dotenv import load_dotenv

# File Paths
ZEROG_DIR = os.path.expanduser("~/.zerog")
THREADS_DIR = os.path.join(ZEROG_DIR, "threads")
SETTINGS_FILE = os.path.join(ZEROG_DIR, "settings.json")
LOGS_DIR = os.path.join(ZEROG_DIR, "logs")

# Load environment variables from ~/.zerog/.env first
env_path = os.path.join(ZEROG_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0")) if os.getenv("ALLOWED_USER_ID") else 0
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

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

# Discord Webhook Handler
import urllib.request
import json

class DiscordWebhookHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url

    def emit(self, record):
        try:
            log_entry = self.format(record)
            payload = {
                "content": f"**[{record.levelname}]** ZeroG Alert\n```\n{log_entry}\n```"
            }
            req = urllib.request.Request(
                self.webhook_url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json', 'User-Agent': 'ZeroG-Bot'}
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            # We silently drop exceptions here to prevent recursive logging loops if webhook fails
            pass

if DISCORD_WEBHOOK_URL:
    wh = DiscordWebhookHandler(DISCORD_WEBHOOK_URL)
    wh.setLevel(logging.WARNING)  # Send only WARNING and ERROR to Discord
    wh.setFormatter(formatter)
    logger.addHandler(wh)
