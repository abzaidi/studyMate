# main.py

import os
from pdf_to_images import convert_pdf_to_images, image_to_byte_array
from text_extraction import extract_text_from_image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if google_credentials_path is None:
    raise ValueError("The environment variable 'GOOGLE_APPLICATION_CREDENTIALS' is not set.")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_path

def process_pdf(pdf_path, output_text_file):
    # Convert PDF to images
    images = convert_pdf_to_images(pdf_path)

    all_text = ""

    for i, image in enumerate(images):
        # Convert image to byte array
        img_byte_arr = image_to_byte_array(image)

        # Extract text from image
        text = extract_text_from_image(img_byte_arr)
        all_text += f"Page {i + 1}:\n{text}\n\n"

    # Save all the extracted text to a single file
    with open(output_text_file, 'w', encoding="UTF-8") as file:
        file.write(all_text)

    print(f"Text extracted and saved to {output_text_file}")

if __name__ == "__main__":
    # Path to the PDF document
    pdf_path = 'pp.pdf'

    # Path to save the extracted text
    output_text_file = 'extracted_text.txt'

    # Process the PDF and extract text
    process_pdf(pdf_path, output_text_file)
