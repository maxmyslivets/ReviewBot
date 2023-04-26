import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEBUG = True if os.getenv("DEBUG") == 'True' else False
TG_TOKEN = str(os.getenv("TG_TOKEN"))
TG_DEV_ADMIN_ID = int(os.getenv("TG_DEV_ADMIN_ID"))
TG_ADMIN_ID = int(os.getenv("TG_ADMIN_ID"))

BASE_DIR = Path(__file__).resolve().parent
