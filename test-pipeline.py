from ocr_engine import extract_text
from llm_engine import explain_document

# Step 1: Extract text from the report using OCR
filepath = "report1.jpg"
extracted_text = extract_text(filepath)

print("=" * 50)
print("EXTRACTED TEXT (from OCR):")
print("=" * 50)
print(extracted_text)

# Step 2: Send extracted text to the local LLM for explanation
print("\n" + "=" * 50)
print("LLM EXPLANATION:")
print("=" * 50)

explanation = explain_document(extracted_text, user_question="What does this liver function test report mean?")
print(explanation)