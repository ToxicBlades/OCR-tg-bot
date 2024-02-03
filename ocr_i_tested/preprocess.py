import cv2
import numpy as np
from PIL import Image
import tempfile

# Function to normalize the image
def normalize_image(image):
    norm_img = np.zeros((image.shape[0], image.shape[1]))
    return cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)

# Function to correct skew in the image
def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray > 0))
    coords = np.float32(coords)  # Convert coords to float32
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
# Function to scale the image
def set_image_dpi(file_path):
    im = Image.open(file_path)
    length_x, width_y = im.size
    factor = min(1, float(1024.0 / length_x))
    size = int(factor * length_x), int(factor * width_y)
    im_resized = im.resize(size, Image.ANTIALIAS)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_filename = temp_file.name
    im_resized.save(temp_filename, dpi=(300, 300))
    return temp_filename

# Function to remove noise
def remove_noise(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)

# Function to convert to grayscale
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Function to apply thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Main function to preprocess the image
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = normalize_image(image)
    image = deskew(image)
    image_dpi_path = set_image_dpi(image_path)
    image = cv2.imread(image_dpi_path)
    image = remove_noise(image)
    image = get_grayscale(image)
    image = thresholding(image)

    # preprocessed_image_path = 'preprocessed_image.jpg'
    # cv2.imwrite(preprocessed_image_path, image)
    # return preprocessed_image_path

    return image

