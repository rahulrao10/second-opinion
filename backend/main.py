from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile, os

from ocr_engine import extract_text
from llm_engine import explain_document, PatientMemory

app = FastAPI(title="Second Opinion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {
    "extracted_text": None,
    "doc_name": None,
    "chat_history": [],
    "patient_memory": PatientMemory(),
}


class ChatRequest(BaseModel):
    question: str


class ChatMessage(BaseModel):
    role: str
    content: str


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.unlink(tmp_path)

    # Archive previous document into memory before replacing it
    if sessions["extracted_text"]:
        sessions["patient_memory"].add_fact(
            f"Previous report '{sessions['doc_name']}': {sessions['extracted_text'][:200]}"
        )

    sessions["extracted_text"] = text
    sessions["doc_name"] = file.filename
    sessions["chat_history"] = []

    return {"filename": file.filename, "extracted_text": text}


@app.post("/chat")
async def chat(req: ChatRequest):
    if not sessions["extracted_text"]:
        raise HTTPException(status_code=400, detail="No document uploaded yet")

    answer = explain_document(
        sessions["extracted_text"],
        sessions["chat_history"],
        req.question,
        patient_memory=sessions["patient_memory"],
    )

    sessions["chat_history"].append(("user", req.question))
    sessions["chat_history"].append(("assistant", answer))

    return {"answer": answer}


@app.get("/history")
async def get_history():
    return {
        "doc_name": sessions["doc_name"],
        "chat_history": [{"role": r, "content": c} for r, c in sessions["chat_history"]],
    }


@app.post("/reset")
async def reset_session():
    sessions["extracted_text"] = None
    sessions["doc_name"] = None
    sessions["chat_history"] = []
    return {"status": "cleared"}


@app.get("/health")
async def health():
    return {"status": "ok"}