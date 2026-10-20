import os
import re
import subprocess

import pytesseract
from PIL import Image, ImageEnhance, ImageOps
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\poppler\poppler-26.09.0\Library\bin'


def preprocess_image(image):
    """Upscale, grayscale, contrast, sharpen, autocontrast."""
    width, height = image.size
    if width < 1800:
        scale = 1800 / width
        image = image.resize((int(width * scale), int(height * scale)), Image.LANCZOS)

    image = image.convert('L')
    image = ImageEnhance.Contrast(image).enhance(1.8)
    image = ImageEnhance.Sharpness(image).enhance(1.5)
    image = ImageOps.autocontrast(image)
    return image


def extract_text_from_image(image_path):
    image = Image.open(image_path)
    image = preprocess_image(image)
    return pytesseract.image_to_string(image, config=r'--oem 3 --psm 6')


def extract_native_text(pdf_path):
    """Reads the PDF's embedded text layer using Poppler's pdftotext."""
    exe = os.path.join(POPPLER_PATH, 'pdftotext.exe')
    r = subprocess.run([exe, '-layout', pdf_path, '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return r.stdout


def _tokens(text):
    return re.findall(r'[A-Za-z0-9\.\-/%]+', text.lower())


def extract_text_from_pdf(pdf_path):
    """Uses the embedded text layer if present (digital PDF); otherwise OCRs each page."""
    native = extract_native_text(pdf_path)
    if len(_tokens(native)) > 30:
        return native

    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH, dpi=300)
    full_text = ""
    for i, page in enumerate(pages):
        page = preprocess_image(page)
        page_text = pytesseract.image_to_string(page, config=r'--oem 3 --psm 6')
        full_text += f"\n--- Page {i + 1} ---\n{page_text}"
    return full_text


def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext in ['.jpg', '.jpeg', '.png']:
        return extract_text_from_image(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please use PDF, JPG, JPEG, or PNG.")


if __name__ == "__main__":
    print(extract_text("report1.jpg"))