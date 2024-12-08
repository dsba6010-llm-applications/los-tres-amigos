#to pull this from anywhere
#from data_processing.pdf_text_processing import process_pdf_text
import re

def clean_text(text):
    # Remove unwanted characters (keep letters, numbers, and basic punctuation)
    text = re.sub(r'[^a-zA-Z0-9.,!?\'\"\-() ]+', '', text)
    # Normalize multiple spaces to a single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def remove_headers_footers(text):
    # Example: Remove patterns like 'Page 1 of 10'
    text = re.sub(r'Page \d+ of \d+', '', text)
    # Add additional patterns as needed
    return text


def normalize_spacing(text):
    return ' '.join(text.split())


def preprocess_text(text):
    text = clean_text(text)
    text = remove_headers_footers(text)
    text = normalize_spacing(text)
    return text
