import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # For text-only input, use the 'gemini-pro' model
    model = genai.GenerativeModel('gemini-2.0-flash') # Ganti dengan nama model yang Anda temukan
else:
    logger.error("GEMINI_API_KEY not found in environment variables. Please set it.")
    exit()

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        'Halo! Saya adalah bot Telegram yang ditenagai oleh Gemini API. '
        'Kirimkan saya pesan dan saya akan mencoba menjawabnya!'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message when the /help command is issued."""
    await update.message.reply_text(
        'Saya bisa menjawab pertanyaan Anda. Cukup ketik pesan Anda.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes user messages and sends them to Gemini API for a response."""
    user_message = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"Received message from chat_id {chat_id}: {user_message}")

    if not user_message:
        return

    try:
        # Send message to Gemini API
        response = model.generate_content(user_message)
        gemini_reply = response.text
        logger.info(f"Gemini responded: {gemini_reply}")

        # Send Gemini's response back to the user
        await update.message.reply_text(gemini_reply)

    except Exception as e:
        logger.error(f"Error communicating with Gemini API: {e}")
        await update.message.reply_text(
            "Maaf, saya mengalami masalah saat memproses permintaan Anda. "
            "Silakan coba lagi nanti."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a user-friendly message."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')
    if update.effective_message:
        await update.effective_message.reply_text(
            "Terjadi kesalahan. Silakan coba lagi."
        )

def main() -> None:
    """Starts the bot."""
    # Create the Application and pass it your bot's token.
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables. Please set it.")
        return

    # Inisialisasi Application dengan token bot Anda
    # Ini adalah cara yang benar untuk memastikan bot diinisialisasi
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot started. Press Ctrl-C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()