# -*- coding: utf-8 -*-
import requests
import re
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
from pillow_heif import register_heif_opener

register_heif_opener() # to detect if its heic

import tinify


load_dotenv()
OCR_API = os.getenv("OCR_API")
TINIFY_API_KEY = os.getenv("TINIFY_API_KEY")

tinify.key = TINIFY_API_KEY


MAX_FILE_SIZE_MB = 1 * 1024 * 1024  # 1MB in Bytes

def ocr_space_file(filename, overlay=False, api_key=OCR_API, language='eng'):
    """
    Calling to ocr space api for OCR
    API_KEY should be in your .env or config.py
    language parameter allows you to chose which lang you need to ocr(can be auto)
    You can see whole response deleting parsed_text variable and just print result
    """

    if os.path.getsize(filename) > MAX_FILE_SIZE_MB:
        print(f"Original file size is larger than 1MB, compressing {filename}...")

        source = tinify.from_file(filename)
        source.to_file(filename)



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
    os.remove(filename)
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





# print(ocr_space_file('./src/test.JPG'))