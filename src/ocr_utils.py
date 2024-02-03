import requests
import re
from dotenv import load_dotenv
import os

load_dotenv()
OCR_API = os.getenv("OCR_API")

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

def extract_email_from_ocr_result(ocr_result):
    if not isinstance(ocr_result, str):
        raise TypeError("Input must be a string")

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, ocr_result)

    if match:
        return match.group()
    else:
        return None
