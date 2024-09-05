import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from pathlib import Path
import uuid
from dotenv import load_dotenv
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def save_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('recv image')

    new_file = await update.message.effective_attachment[-1].get_file()


    path = Path(__file__).parent / 'downloaded_images' / f'{uuid.uuid4()}.jpg'
    file = await new_file.download_to_drive(custom_path=path)
    print(file)

    
if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    
    image_handler = MessageHandler(filters.PHOTO, save_image)

    application.add_handler(start_handler)
    application.add_handler(image_handler)
    
    application.run_polling()