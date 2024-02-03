import telebot
from config import OCR_API, TESTBOTKEY, SMTP_MAIL , SMTP_PASS
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
TOKEN = TESTBOTKEY
bot = telebot.TeleBot(TOKEN)
# Predefined Excel file details
PREDEFINED_EXCEL_FILENAME = "test.xlsx"


# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = SMTP_MAIL
SMTP_PASSWORD = SMTP_PASS


def extract_email_from_ocr_result(ocr_result):
    # Use regular expression to find and extract email address
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, ocr_result)

    if match:
        return match.group()
    else:
        return None

def send_email(receiver_email, attachment_path=None):
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

def ocr_space_file(filename, overlay=False, api_key=OCR_API, language='eng'):
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

def handle_document(message):
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
        bot.reply_to(message, "Error processing document. Please try again.")


    finally:
        # Delete the temporary file
        try:
            os.remove(document_filename)
        except Exception as e:
            print(f"Error deleting document file: {e}")

@bot.message_handler(content_types=['document'])
def handle_document_message(message):
    handle_document(message)

if __name__ == "__main__":
    bot.polling(none_stop=True)
