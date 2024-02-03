import pytesseract
from PIL import Image, ImageFilter, ImageEnhance

from ocr_i_tested.preprocess import preprocess_image
# Path to tesseract executable
# For Windows, it's usually something like 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def extract_text_from_image(image_path):
    try:
        img = preprocess_image(image_path)
        text = pytesseract.image_to_string(img)
        return text


    except Exception as e:
        return str(e)

# Example usage
image_path = 'C:\\Users\\Asus\Desktop\\all for work\\OCR\\test_photo\\test2.jpg'
extracted_text = extract_text_from_image(image_path)
print(extracted_text)