# main.py

import os
from pdf_to_images import convert_pdf_to_images, image_to_byte_array
from text_extraction import extract_text_from_image
from text_cleaning import correct_grammar_and_context
from dotenv import load_dotenv, find_dotenv
from PIL import Image

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if google_credentials_path is None:
    raise ValueError("The environment variable 'GOOGLE_APPLICATION_CREDENTIALS' is not set.")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_path

def process_file(file_path, output_text_file):
    all_text = ""

    # Check if the file is a PDF or an image
    if file_path.lower().endswith('.pdf'):
        # Convert PDF to images
        images = convert_pdf_to_images(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Open the image file
        images = [Image.open(file_path)]
    else:
        raise ValueError("Unsupported file format. Please provide a PDF, PNG, or JPG file.")

    for i, image in enumerate(images):
        # Convert image to byte array
        img_byte_arr = image_to_byte_array(image)

        # Extract text from image
        text = extract_text_from_image(img_byte_arr)

        # Clean the extracted text
        # text = normalize_text(text)
        # text = correct_spelling(text)
        text = correct_grammar_and_context(text)


        all_text += f"Page {i + 1}:\n{text}\n\n"

    # Save all the extracted text to a single file
    with open(output_text_file, 'w', encoding="UTF-8") as file:
        file.write(all_text)

    print(f"Text extracted and saved to {output_text_file}")

if __name__ == "__main__":
    # Path to the file (PDF or image)
    file_path = 'comp.jpg'

    # Path to save the extracted text
    output_text_file = 'extracted_text.txt'

    # Process the file and extract text
    process_file(file_path, output_text_file)