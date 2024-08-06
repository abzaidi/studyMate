# pdf_to_images.py

from pdf2image import convert_from_path
import io

def convert_pdf_to_images(pdf_path):
    try:
        return convert_from_path(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Error converting PDF to images: {e}")

def image_to_byte_array(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
