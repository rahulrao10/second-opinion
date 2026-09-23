import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

# Point to your Tesseract install location (adjust if different)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Point to your Poppler bin folder (adjust to wherever you extracted it)
POPPLER_PATH = r'"C:\poppler\poppler-26.09.0\Library\bin"'


def extract_text_from_image(image_path):
    """
    Extracts text from a single image file (jpg, jpeg, png).
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def extract_text_from_pdf(pdf_path):
    """
    Converts each page of a PDF into an image, then runs OCR on each page.
    Returns combined text from all pages.
    """
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    full_text = ""
    for i, page in enumerate(pages):
        page_text = pytesseract.image_to_string(page)
        full_text += f"\n--- Page {i + 1} ---\n{page_text}"
    return full_text


def extract_text(filepath):
    """
    Main entry point — detects file type and routes to the right extractor.
    Supports: .pdf, .jpg, .jpeg, .png
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext in ['.jpg', '.jpeg', '.png']:
        return extract_text_from_image(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please use PDF, JPG, JPEG, or PNG.")


# Quick test
if __name__ == "__main__":
    test_file = "report1.jpg"  # change this to test different file types
    extracted = extract_text(test_file)
    print("Extracted text:")
    print(extracted)