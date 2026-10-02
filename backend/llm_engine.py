import ollama
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

# ---- Conversation memory (vector-based retrieval over chat history) ----

def get_relevant_history(question, chat_history, top_k=3):
    """
    Retrieves the most semantically relevant past messages (not just recent ones)
    using the same TF-IDF + cosine similarity approach from the RAG pipeline.
    chat_history: list of (role, message) tuples.
    """
    if len(chat_history) == 0:
        return []

    message_texts = [msg for role, msg in chat_history]

    # Not enough messages to bother vectorizing meaningfully
    if len(message_texts) < 2:
        return chat_history

    vectorizer = TfidfVectorizer(stop_words='english')
    history_vectors = vectorizer.fit_transform(message_texts)
    question_vector = vectorizer.transform([question])

    similarities = cosine_similarity(question_vector, history_vectors)[0]
    top_indices = similarities.argsort()[::-1][:top_k]
    top_indices = sorted(top_indices)  # preserve chronological order in output

    return [chat_history[i] for i in top_indices]


# ---- Parent memory (persistent patient facts, always included) ----

class PatientMemory:
    """
    Holds important facts about the patient that should ALWAYS be included
    in context, regardless of conversation length — e.g. known conditions,
    allergies, or key values extracted from earlier reports.
    """
    def __init__(self):
        self.facts = []  # list of strings

    def add_fact(self, fact_text):
        if fact_text not in self.facts:
            self.facts.append(fact_text)

    def get_facts_text(self):
        if not self.facts:
            return ""
        return "Known patient facts (always relevant):\n" + "\n".join(f"- {f}" for f in self.facts)

    def remove_fact(self, fact_text):
        if fact_text in self.facts:
            self.facts.remove(fact_text)

def explain_document(extracted_text, chat_history, user_question, patient_memory=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 1. Parent memory — always included, regardless of conversation length
    if patient_memory:
        facts_text = patient_memory.get_facts_text()
        if facts_text:
            messages.append({"role": "system", "content": facts_text})

    # 2. Current document
    messages.append({"role": "user", "content": f"Current document:\n{extracted_text}"})

    # 3. Relevant past conversation (retrieved, not just recent)
    relevant_history = get_relevant_history(user_question, chat_history, top_k=3)
    for role, msg in relevant_history:
        messages.append({"role": role, "content": msg})

    # 4. The new question
    messages.append({"role": "user", "content": user_question})

    response = ollama.chat(
        model="llama3.2:3b",
        messages=messages,
        options={"temperature": 0.3, "num_predict": 180}
    )
    return response['message']['content']
