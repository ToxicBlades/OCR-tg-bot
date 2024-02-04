# -*- coding: utf-8 -*-
import telebot
from telebot import types
from email_utils import send_email
from ocr_utils import ocr_space_file, extract_email_from_ocr_result
from gpt_text_to_json import process_ai
import os
import time
import re

from dotenv import load_dotenv
load_dotenv()
TESTBOTKEY = os.getenv("TESTBOTKEY")
CHAT_TEST = os.getenv("CHAT_TEST")
WHITE_LIST = os.getenv("WHITE_LIST")
WHITE_LIST = [int(item) for item in WHITE_LIST.split(',')]

TOKEN = TESTBOTKEY
bot = telebot.TeleBot(TOKEN)
PREDEFINED_EXCEL_FILENAME = "./data/test.xlsx"
user_states = {}  # Tracks the current action/state of each user


def start_bot():
    try:
        bot.polling(True)
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")
        print("Restarting the bot...")
        time.sleep(30)
        start_bot()


def process_new_value(message, credential_type):
    """
    Function to process the new value entered by the user and update the .env
    """
    chat_id = message.chat.id
    new_value = message.text.strip()


    try:
        with open('.env', 'r') as config_file:
            config_content = config_file.read()

        if credential_type == 'change_password':
            config_content = re.sub(r'SMTP_PASS\s*=\s*["\'].+["\']', f'SMTP_PASS = "{new_value}"', config_content)
        elif credential_type == 'change_email':
            config_content = re.sub(r'SMTP_MAIL\s*=\s*["\'].+["\']', f'SMTP_MAIL = "{new_value}"', config_content)
        else:
            bot.reply_to(message, "Invalid credential type. Please use change_password or change_email.")
            return

        with open('.env', 'w') as config_file:
            config_file.write(config_content)

        bot.reply_to(message, f"{credential_type.replace('_', ' ')} прошло успешно.")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

def process_ocr_document(message):

    try:
            # Get the file ID of the document
            file_id = message.document.file_id

            # Download the document
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Save the document
            document_filename = f"temp_document_{file_id}.jpg"
            with open(document_filename, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Perform OCR on the saved document
            ocr_result = ocr_space_file(document_filename)

            json_text = process_ai(ocr_result)

            # Send the OCR result back to the user
            bot.reply_to(message, f"OCR Result:\n{ocr_result}\n{json_text}")

            # Send an email with
            receiver_email = extract_email_from_ocr_result(ocr_result)
            excel_attachment_path = PREDEFINED_EXCEL_FILENAME
            send_email(bot, receiver_email, attachment_path=excel_attachment_path)

    except Exception as e:
            print(f"Error processing document: {e}")
            bot.reply_to(message, "Error processing document. Please try again later.")
    finally:
        try:
            os.remove(document_filename)
        except Exception as e:
            print(f"Error deleting document file: {e}")

def process_excel_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        save_path = PREDEFINED_EXCEL_FILENAME

        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Эксель файл успешно обновлён.")
    except Exception as e:
            bot.reply_to(message, f"Не получилось установить эксель,попробойти позже: {e}")


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    #bot.send_message(chat_id,f'your chat id is {chat_id}')
    bot.reply_to(message, "Это OCR бот который распознает вашу визику и отправит фоллоу ап для вашего клиента. отправляйте мне только файлы")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """
    Simple function where we download doccument by its id.
    Then OCR it send our result to chat
    Sending an email after
    """
    chat_id = message.chat.id
    current_state = user_states.get(chat_id)
    if current_state == 'change_excel':
        process_excel_document(message)
        user_states[chat_id] = None
    else:
        process_ocr_document(message)
        user_states[chat_id] = None

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """
    Function to handle when a user sends a photo.
    Replies with a message asking the user to send a document instead.
    """
    bot.reply_to(message, "Пожалуйста отправьте мне фото как доккумент.")

@bot.message_handler(commands=['change_credentials'])
def handle_change_credentials(message):
    """
    Function to handle the /change_credentials command.
    Allows the user to change SMTP_MAIL or SMTP_PASS in config.py.
    """
    chat_id = message.chat.id

    # Check if the user is authorized to change credentials (optional)
    authorized_users = WHITE_LIST # Add authorized chat IDs
    if chat_id not in authorized_users:
        bot.reply_to(message, "Вы не авторизованны чтобы изменять данные.")
        return
    # Display three buttons
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    change_pass_button = types.KeyboardButton('Change Password')
    change_email_button = types.KeyboardButton('Change Email')
    cancel_button = types.KeyboardButton('Cancel')
    keyboard.add(change_pass_button, change_email_button, cancel_button)

    bot.send_message(chat_id, "Выберите опцию:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text in ['Change Password', 'Change Email', 'Cancel'])
def handle_change_credentials_choice(message):
    """
    Function to handle user's choice after displaying buttons.
    """
    chat_id = message.chat.id

    if message.text == 'Cancel':
        bot.reply_to(message, "Операция отменена.")
        return

    # Get the command parameters
    credential_type = message.text.lower().replace(' ', '_')

    # Handle the chosen option accordingly
    if credential_type in ['change_password', 'change_email']:
        bot.reply_to(message, f"Вы выбрали:  {credential_type.replace('_', ' ')}.")

        # Ask the user for the new value
        bot.send_message(chat_id, f"Пожалуйста введите новое значение:")
        bot.register_next_step_handler(message, lambda msg: process_new_value(msg, credential_type))

    else:
        bot.reply_to(message, "Неправельный выбор. Пожалуйста выберите существующую опцию.")


@bot.message_handler(commands=['change_excel'])
def handle_change_excel(message):
    chat_id = message.chat.id
    # Here, add your authorization check if needed
    if chat_id in WHITE_LIST:
        user_states[chat_id] = 'change_excel'
        bot.send_message(chat_id, "Please upload the new Excel file.")
    else:
        bot.reply_to(message, "You are not authorized to perform this action.")