# text_extraction.py

from google.cloud import vision

def extract_text_from_image(image_content):
    # Initialize the Vision API client
    client = vision.ImageAnnotatorClient()

    # Construct an image instance
    image = vision.Image(content=image_content)

    # Perform text detection
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # Extract the detected text
    if texts:
        extracted_text = texts[0].description
    else:
        extracted_text = ""

    # Handle possible errors
    if response.error.message:
        raise Exception(f'{response.error.message}')

    return extracted_text
