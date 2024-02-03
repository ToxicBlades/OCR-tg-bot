import telebot
from telebot import types
from config import OCR_API, TESTBOTKEY, SMTP_MAIL , SMTP_PASS, CHAT_TEST, WHITE_LIST
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
import threading
import time
TOKEN = TESTBOTKEY
bot = telebot.TeleBot(TOKEN)
# Predefined Excel file details
PREDEFINED_EXCEL_FILENAME = "test.xlsx"


# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = SMTP_MAIL
SMTP_PASSWORD = SMTP_PASS


def start_bot():
    """
    The main scope of this function is to put it on thread
    so bot never stop working if he ison server.
    If interenet shots down for a second bot will die,
    but in 30 seconds this function will recover him
    """
    try:
        bot.polling(True)
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")
        print("Restarting the bot...")
        time.sleep(30)
        start_bot()


def extract_email_from_ocr_result(ocr_result):
    if not isinstance(ocr_result, str):
        raise TypeError("Input must be a string")

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, ocr_result)

    if match:
        return match.group()
    else:
        return None


def send_email(receiver_email, attachment_path=None):
    """
    Connecting to gmail smtp using email and app password
    Adding attachment if provided
    And then send email with prededicated text, subject.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = receiver_email
        msg['Subject'] = 'This is sam global trading'
        msg.attach(MIMEText('This is our offers to you', 'plain'))

        # Attach Excel file if provided
        if attachment_path:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
                msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, receiver_email, msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        # Handle the case where credentials are outdated
        bot.send_message(chat_id=CHAT_TEST, text='Please update your credentials of OCR BOT.He cant send emails at the moment')



def ocr_space_file(filename, overlay=False, api_key=OCR_API, language='eng'):
    """
    Calling to ocr space api for OCR
    API_KEY should be in your .env or config.py
    language parameter allows you to chose which lang you need to ocr(can be auto)
    You can see whole response deleting parsed_text variable and just print result
    """
    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )

    result_json = r.json()
    parsed_text = result_json['ParsedResults'][0]['ParsedText']
    return parsed_text

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """
    Simple function where we download doccument by its id.
    Then OCR it send our result to chat
    Sending an email after
    """
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

        # Send the OCR result back to the user
        bot.reply_to(message, f"OCR Result:\n{ocr_result}")

        # Send an email with
        receiver_email = extract_email_from_ocr_result(ocr_result)
        excel_attachment_path = PREDEFINED_EXCEL_FILENAME
        send_email(receiver_email, attachment_path=excel_attachment_path)

    except Exception as e:
        print(f"Error processing document: {e}")
        bot.reply_to(message, "Error processing document. Please try again later.")


    finally:
        # Delete the temporary file
        try:
            os.remove(document_filename)
        except Exception as e:
            print(f"Error deleting document file: {e}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    """
    Function to handle the /start command.
    Sends a welcome message to the user.
    """
    chat_id = message.chat.id
    bot.send_message(chat_id,f'your chat id is {chat_id}')
    bot.reply_to(message, "Это OCR бот который распознает вашу визику и отправит фоллоу ап для вашего клиента. отправляйте мне только файлы")

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


def process_new_value(message, credential_type):
    """
    Function to process the new value entered by the user and update the config.
    """
    chat_id = message.chat.id
    new_value = message.text.strip()

    # Update the corresponding credential in config.py
    try:
        with open('config.py', 'r') as config_file:
            config_content = config_file.read()

        if credential_type == 'change_password':
            config_content = re.sub(r'SMTP_PASS\s*=\s*["\'].+["\']', f'SMTP_PASS = "{new_value}"', config_content)
        elif credential_type == 'change_email':
            config_content = re.sub(r'SMTP_MAIL\s*=\s*["\'].+["\']', f'SMTP_MAIL = "{new_value}"', config_content)
        else:
            bot.reply_to(message, "Invalid credential type. Please use change_password or change_email.")
            return

        with open('config.py', 'w') as config_file:
            config_file.write(config_content)

        bot.reply_to(message, f"{credential_type.replace('_', ' ')} прошло успешно.")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")


if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
