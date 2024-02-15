# -*- coding: utf-8 -*-
import requests
import re
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
from pillow_heif import register_heif_opener

register_heif_opener() # to detect if its heic

load_dotenv()
OCR_API = os.getenv("OCR_API")

MAX_FILE_SIZE_MB = 1 * 1024 * 1024  # 1MB in Bytes

def compress_image(image_path, output_path=None, quality=35):
    """
    Compresses an image or converts it from HEIC to JPEG if necessary, then reduces its file size to be less than 1 MB.
    """
    # Open the image using Pillow, which now supports HEIC through Pillow-Heif
    img = Image.open(image_path)
    img_format = 'JPEG'  # We default to JPEG for output

    # If an output path wasn't specified, generate one based on the input path
    if not output_path:
        base, _ = os.path.splitext(image_path)
        output_path = f"{base}.jpeg"

    img_bytes = BytesIO()
    img.save(img_bytes, format=img_format, quality=quality, optimize=True)

    # More aggressive quality reduction and resizing if necessary
    while img_bytes.tell() > MAX_FILE_SIZE_MB:
        img_bytes.seek(0)  # Reset the BytesIO object
        quality -= 10  # Decrease quality in larger steps
        if quality <= 20:
            # If quality is already low, start resizing
            scale_factor = (MAX_FILE_SIZE_MB / img_bytes.tell()) ** 0.5
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
            quality = 75  # Reset quality for resized image
        img.save(img_bytes, format=img_format, quality=quality, optimize=True)

    img_bytes.seek(0)  # Go back to the start of the BytesIO object
    with open(output_path, 'wb') as f:
        f.write(img_bytes.getvalue())  # Write the final compressed image to disk

    return output_path


def ocr_space_file(filename, overlay=False, api_key=OCR_API, language='eng'):
    """
    Calling to ocr space api for OCR
    API_KEY should be in your .env or config.py
    language parameter allows you to chose which lang you need to ocr(can be auto)
    You can see whole response deleting parsed_text variable and just print result
    """

    if os.path.getsize(filename) > MAX_FILE_SIZE_MB:
        print(f"Original file size is larger than 1MB, compressing {filename}...")
        filename = compress_image(filename)



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
