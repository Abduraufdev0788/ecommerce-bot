import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

CARD_NUMBER = os.getenv("CARD_NUMBER")
CARD_OWNER = os.getenv("CARD_OWNER")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

