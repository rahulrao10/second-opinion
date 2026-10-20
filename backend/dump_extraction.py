import os
import sys
import pytesseract
from pdf2image import convert_from_path
from ocr_engine import (extract_native_text, preprocess_image,
                        POPPLER_PATH, _tokens)


def ocr_with_flags(pdf_path, conf_threshold=80):
    """OCR every page; words below the threshold are marked like word[?62]."""
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH, dpi=300)
    out = []
    for i, page in enumerate(pages):
        img = preprocess_image(page)
        d = pytesseract.image_to_data(img, config='--oem 3 --psm 6',
                                      output_type=pytesseract.Output.DICT)
        lines = {}
        for j, w in enumerate(d['text']):
            if not w.strip():
                continue
            conf = float(d['conf'][j])
            key = (d['block_num'][j], d['par_num'][j], d['line_num'][j])
            token = w if conf >= conf_threshold else f"{w}[?{int(conf)}]"
            lines.setdefault(key, []).append(token)
        out.append(f"\n--- Page {i + 1} ---")
        out.extend(" ".join(words) for _, words in sorted(lines.items()))
    return "\n".join(out)


if __name__ == "__main__":
    pdf = sys.argv[1]
    base = os.path.splitext(os.path.basename(pdf))[0]

    native = extract_native_text(pdf)
    if len(_tokens(native)) > 30:
        with open(f"{base}_native.txt", "w", encoding="utf-8") as f:
            f.write(native)
        print(f"Saved {base}_native.txt (embedded text layer)")
    else:
        print("No text layer found (scanned PDF), skipping native dump")

    with open(f"{base}_ocr.txt", "w", encoding="utf-8") as f:
        f.write(ocr_with_flags(pdf))
    print(f"Saved {base}_ocr.txt (forced OCR, shaky words marked [?confidence])")