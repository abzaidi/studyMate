import cv2
import pytesseract

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'G:\Tesseract OCR\tesseract.exe'  # Adjust the path as needed

def preprocess_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to binarize the image
    _, thresh_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

    # Optionally, apply noise removal techniques
    processed_image = cv2.medianBlur(thresh_image, 3)

    return processed_image

def extract_text_from_image(image_path):
    # Preprocess the image
    processed_image = preprocess_image(image_path)

    # Perform OCR on the processed image
    extracted_text = pytesseract.image_to_string(processed_image, lang='eng', config='--psm 6')

    return extracted_text

# Path to the handwritten note image
image_path = 'notes.jpg'

# Extract text from the image
text = extract_text_from_image(image_path)

# Print the extracted text
with open('extracted_text.txt', 'w') as file:
    file.write(text)

print("Text extracted and saved to extracted_text.txt")
