import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN', '8990165115:AAF5pSg9jXtu8XqpyGSWDW6GvoiMtqipPsE')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')

# Flask
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'