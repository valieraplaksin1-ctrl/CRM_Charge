import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN', '8990165115:AAF5pSg9jXtu8XqpyGSWDW6GvoiMtqipPsE')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')

# Flask
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'

print(f"✅ Конфигурация загружена:")
print(f"   BOT_TOKEN: {BOT_TOKEN[:20]}...")
print(f"   WEB_APP_URL: {WEB_APP_URL}")
print(f"   FLASK_ENV: {FLASK_ENV}")