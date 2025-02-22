from google.cloud import storage
from django.conf import settings

def upload_to_gcs(file_name, text_content):
    """Uploads extracted text file to Google Cloud Storage and returns its URL."""
    client = storage.Client()
    bucket = client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
    object_name = f"extracted_texts/{file_name}.txt"  # Store as text file

    blob = bucket.blob(object_name)
    blob.upload_from_string(text_content, content_type="text/plain")

    return object_name


def fetch_text_from_gcs(gcs_path):
    """Retrieve text from a GCS object"""
    client = storage.Client()
    bucket = client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(gcs_path)

    if not blob.exists():
        raise FileNotFoundError(f"No such object in GCS: {gcs_path}")

    # Download the text content
    extracted_text = blob.download_as_text()
    return extracted_text
