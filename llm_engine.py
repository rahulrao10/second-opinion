import ollama

SYSTEM_PROMPT = """You are a medical document explainer. Give brief, direct, genuinely useful explanations — not long essays.

RULES:
- Keep answers SHORT: 3-5 sentences max, unless the user explicitly asks for more detail
- Be specific and confident about established medical facts (e.g., what a test measures, what high/low commonly indicates)
- State clearly if a value is high, low, or normal vs. the reference range
- Do NOT diagnose the specific patient or recommend treatment/medication
- Do NOT repeat disclaimers mid-answer — just answer directly
- End with one short line: "Educational purposes only — consult your doctor."
- No long intros, no repeating the question back, no excessive hedging
"""

def explain_document(extracted_text, user_question=""):
    """
    Sends the OCR-extracted text to the local LLM for a plain-language explanation.
    """
    prompt = f"""Here is the extracted text from a medical document:

{extracted_text}

User's question: {user_question if user_question else "Please explain this document in simple terms."}
"""

    response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    options={
        "temperature": 0.3,
        "num_predict": 180    # caps response length — forces brevity, speeds up generation
    }
    )
    return response['message']['content']

# Quick test
if __name__ == "__main__":
    sample_text = "Hemoglobin: 10.2 g/dL (Reference: 13.5-17.5 g/dL)\nWBC Count: 7500/uL (Reference: 4500-11000/uL)"
    result = explain_document(sample_text)
    print(result)