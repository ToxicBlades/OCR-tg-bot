import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

SMTP_MAIL = os.getenv("SMTP_MAIL")
SMTP_PASS = os.getenv("SMTP_PASS")
CHAT_TEST = os.getenv("CHAT_TEST")


# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = SMTP_MAIL
SMTP_PASSWORD = SMTP_PASS

JSON_FILE_PATH = './data/text.json'

def extract_and_replace_from_file (client_name, product_name, company_name,json_file_path=JSON_FILE_PATH,):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    text = json_data["text"]
    theme = json_data["theme"]

    # Extract placeholders from the text
    placeholders = re.findall(r"\bclient_name\b|\bproduct_name\b|\bcompany_name\b", text)

    # Replace placeholders with actual data
    replaced_text = text.replace("client_name", client_name)
    replaced_text = replaced_text.replace("product_name", product_name)

    # Replace placeholders in the theme
    replaced_theme = theme.replace("client_name", client_name)
    replaced_theme = replaced_theme.replace("product_name", product_name)
    replaced_theme = replaced_theme.replace("company_name", company_name)

    return {
        "replaced_text": replaced_text,
        "replaced_theme": replaced_theme,
        "missing_placeholders": list(set(placeholders) - {"client_name", "product_name", "company_name"})
    }

def send_email(bot,receiver_email, attachment_path=None):
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
