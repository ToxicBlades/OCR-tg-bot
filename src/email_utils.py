import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import re
import json
from dotenv import load_dotenv

PREDEFINED_PDF_FILENAME = "./data/sam_global_catalog.pdf"

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

def extract_and_replace_from_json(json_string, json_file_path=JSON_FILE_PATH):
    try:
        json_data = json.loads(json_string)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}

    with open(json_file_path, 'r') as file:
        template_data = json.load(file)

    text = template_data.get("text", "")
    theme = template_data.get("theme", "")

    # Extract placeholders from the text
    placeholders = re.findall(r"\bclient_name\b|\bproduct_name\b|\bcompany_name\b", text)

    # Replace placeholders with actual data
    replaced_text = text.replace("client_name", json_data.get("name", ""))
    replaced_text = replaced_text.replace("product_name", json_data.get(" ", ""))

    # Replace placeholders in the theme
    replaced_theme = theme.replace("client_name", json_data.get("name", ""))
    replaced_theme = replaced_theme.replace("product_name", json_data.get(" ", ""))
    replaced_theme = replaced_theme.replace("company_name", json_data.get("company_name", ""))

    return {
        "replaced_text": replaced_text,
        "replaced_theme": replaced_theme,
        "missing_placeholders": list(set(placeholders) - {"client_name", "product_name", "company_name"})
    }

def send_email(bot,json_text,receiver_email, attachment_path_1=PREDEFINED_PDF_FILENAME, attachment_path_2 = None):
    """
    Connecting to gmail smtp using email and app password
    Adding attachment if provided
    And then send email with prededicated text, subject.
    """
    try:
        data = extract_and_replace_from_json(json_text)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = receiver_email
        msg['Subject'] = data.get("replaced_theme","")
        msg.attach(MIMEText(data.get("replaced_text","")))

        # Attach Excel file if provided
        with open(attachment_path_1, 'rb') as attachment_1:
            part_1 = MIMEBase('application', 'octet-stream')
            part_1.set_payload(attachment_1.read())
            encoders.encode_base64(part_1)
            part_1.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path_1)}"')
            msg.attach(part_1)

        # Attach the second file
        if attachment_path_2:
            with open(attachment_path_2, 'rb') as attachment_2:
                part_2 = MIMEBase('application', 'octet-stream')
                part_2.set_payload(attachment_2.read())
                encoders.encode_base64(part_2)
                part_2.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path_2)}"')
                msg.attach(part_2)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, receiver_email, msg.as_string())

    except smtplib.SMTPAuthenticationError as e:
        # Handle the case where credentials are outdated
        bot.send_message(chat_id=CHAT_TEST, text='Please update your credentials of OCR BOT.He cant send emails at the moment')
