# CareChat

Offline, private medical report explainer. CareChat reads a lab report or prescription
(PDF, JPG or PNG), extracts its text, and explains it in plain language using a local LLM
through Ollama. Nothing leaves your device.

## Project layout

```
CareChat/
  backend/    FastAPI service: OCR / PDF text extraction, LLM, conversation + patient memory
  frontend/   React + TypeScript (Vite) interface
```

`backend/app.py` is the original Streamlit prototype, kept for reference.

## One-time setup

1. Install [Ollama](https://ollama.com/download) and pull the model:
   ```
   ollama pull llama3.2:3b
   ```
2. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) and
   [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases).
   The install paths are set at the top of `backend/ocr_engine.py`
   (`tesseract_cmd` and `POPPLER_PATH`); change them if yours differ.
3. Install Python and Node.js, then the dependencies:
   ```
   cd backend
   pip install -r requirements.txt

   cd ../frontend
   npm install
   ```

## Run

Open two terminals.

```
# Terminal 1: backend (http://localhost:8000)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: frontend (http://localhost:5173)
cd frontend
npm run dev
```

Make sure Ollama is running, then open http://localhost:5173.

## API

| Endpoint | Purpose |
|---|---|
| `POST /upload` | Upload a report (multipart field `file`); returns `filename` and `extracted_text` |
| `POST /chat` | `{ "question": "..." }`; returns `{ "answer": "..." }` |
| `GET /history` | Current document name and chat history |
| `POST /reset` | Clear the current document and chat |
| `GET /health` | Health check |

## Notes

- Session data (document, chat history, patient memory) is held in memory and is lost when the
  backend restarts.
- CareChat explains documents; it does not diagnose or recommend treatment.
