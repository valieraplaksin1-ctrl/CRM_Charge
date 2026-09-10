import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN, WEB_APP_URL
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаём кнопку для открытия Mini App
    keyboard = [
        [
            InlineKeyboardButton(
                "📞 Открыть CRM",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"🎉 Добро пожаловать в CRM для прозвона!\n\n"
        f"Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = (
        "📖 Справка по командам:\n\n"
        "/start - Начать работу с CRM\n"
        "/help - Показать эту справку\n\n"
        "💡 Как пользоваться:\n"
        "1. Нажмите кнопку 'Открыть CRM'\n"
        "2. Введите своё имя\n"
        "3. Управляйте клиентами и прозвонами\n"
    )
    await update.message.reply_text(help_text)

def main() -> None:
    """Запуск бота"""
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Запускаем бота
    logger.info(f"🤖 Бот запущен! Приложение доступно по адресу: {WEB_APP_URL}")
    application.run_polling()

if __name__ == '__main__':
    main()