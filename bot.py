import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image, ImageEnhance
import pytesseract
from preprocess import preprocess_image
from config import INFO_CHAT_ID,TESTBOTKEY,BOTKEY,CHAT_TEST

# Path to tesseract executable
# For Windows, it's usually something like 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Function to extract text from an image
def extract_text_from_image(image_path):
    try:
        img = preprocess_image(image_path)
        text = pytesseract.image_to_string(img)
        return text


    except Exception as e:
        return str(e)

# Callback function for the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Здраствуйте, отправьте мне фото хорошего качества(нормальной освещение и не размытое изображения)')

# Callback function for handling photos
def handle_photo(update: Update, context: CallbackContext) -> None:
    file_id = update.message.photo[-1].file_id
    file = context.bot.get_file(file_id)
    file_path = file.file_path

    # Download the photo
    photo_path = os.path.join('downloads', f'{file_id}.jpg')
    file.download(photo_path)

    # Perform OCR on the downloaded photo
    extracted_text = extract_text_from_image(photo_path)

    # Send the extracted text back to the user
    update.message.reply_text(f'Extracted Text:\n{extracted_text}')

    os.remove(photo_path)

# Main function to start the bot
def main():
    # Set your Telegram bot token here
    token = TESTBOTKEY

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
