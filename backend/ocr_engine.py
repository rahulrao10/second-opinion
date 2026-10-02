import pytesseract
from PIL import Image, ImageEnhance, ImageOps
from pdf2image import convert_from_path
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\poppler\poppler-26.09.0\Library\bin'


def preprocess_image(image):
    """
    Improves image quality before OCR:
    - Upscales small images (bigger text = more accurate recognition)
    - Converts to grayscale (removes color noise)
    - Increases contrast (makes text stand out from background)
    - Sharpens slightly
    """
    # Upscale if too small
    width, height = image.size
    if width < 1800:
        scale = 1800 / width
        image = image.resize((int(width * scale), int(height * scale)), Image.LANCZOS)

    # Convert to grayscale
    image = image.convert('L')

    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.8)

    # Increase sharpness
    sharpener = ImageEnhance.Sharpness(image)
    image = sharpener.enhance(1.5)

    # Auto-adjust brightness levels (stretches contrast range)
    image = ImageOps.autocontrast(image)

    return image


def extract_text_from_image(image_path):
    """
    Extracts text from a single image file (jpg, jpeg, png), with preprocessing.
    """
    image = Image.open(image_path)
    image = preprocess_image(image)

    # PSM 6 = assume a uniform block of text; better for structured reports/tables
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text


def extract_text_from_pdf(pdf_path):
    """
    Converts each page of a PDF into an image, preprocesses it, then runs OCR.
    """
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH, dpi=300)
    full_text = ""
    custom_config = r'--oem 3 --psm 6'

    for i, page in enumerate(pages):
        page = preprocess_image(page)
        page_text = pytesseract.image_to_string(page, config=custom_config)
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
    test_file = "report1.jpg"
    extracted = extract_text(test_file)
    print("Extracted text:")
    print(extracted)