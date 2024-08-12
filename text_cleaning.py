# from transformers import pipeline
import re
from textblob import TextBlob


def correct_spelling(text):
    blob = TextBlob(text)
    corrected_text = str(blob.correct())
    return corrected_text

# def correct_spelling(text):
#     # Use the T5 model for correcting spelling and grammar
#     corrector = pipeline("text2text-generation", model="t5-base")
#     prompt = f"Correct spelling: {text}"
#     corrected = corrector(prompt, max_length=512)
#     return corrected[0]['generated_text']

# def correct_grammar_and_context(text):
#     # Use the T5 model for correcting grammar and context
#     corrector = pipeline("text2text-generation", model="t5-base")
#     prompt = f"Correct grammar and context: {text}"
#     corrected = corrector(prompt, max_length=512)
#     return corrected[0]['generated_text']


def normalize_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters (optional)
    # text = re.sub(r'[^\w\s]', '', text)
    return text