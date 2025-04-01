from google.cloud import storage
from django.conf import settings

def upload_to_gcs(file_name, text_content, file_type="extracted_texts"):
    """
    Uploads a text file (extracted text, quiz, or Q&A) to Google Cloud Storage and returns its GCS path.

    Parameters:
        file_name (str): The base name of the file (without extension).
        text_content (str): The text content to be stored.
        file_type (str): Type of file - "extracted_texts", "quizzes", or "qna".

    Returns:
        str: The GCS object name (path).
    """
    if not text_content:  # Prevent uploading empty/None content
        raise ValueError("Text content cannot be empty or None.")

    client = storage.Client()
    bucket = client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)

    # Ensure correct folder structure
    if file_type not in ["extracted_texts", "quizzes", "qna"]:
        raise ValueError("Invalid file type. Must be 'extracted_texts', 'quizzes', or 'qna'.")

    object_name = f"{file_type}/{file_name}.txt"

    blob = bucket.blob(object_name)
    blob.upload_from_string(text_content, content_type="text/plain")

    return object_name  # Return the GCS path


def fetch_text_from_gcs(gcs_path):
    """
    Retrieves text content from a GCS object.

    Parameters:
        gcs_path (str): The full path of the object in GCS (e.g., "extracted_texts/sample.txt").

    Returns:
        str or None: The retrieved text content, or None if the file does not exist.
    """
    client = storage.Client()
    bucket = client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(gcs_path)

    if not blob.exists():
        return None  # Return None if the file does not exist

    blob.reload()
    return blob.download_as_text() 
