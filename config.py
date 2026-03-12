from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

WHATSAPP_CONTACT_NAME = os.getenv("WHATSAPP_CONTACT_NAME")

IMAP_SERVER = "imap.gmail.com"

MODEL = os.getenv("MODEL")
