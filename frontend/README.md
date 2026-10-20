# CareChat Frontend

React + TypeScript (Vite) interface for CareChat, the offline, privacy-first medical report explainer.

## Run

```
npm install
npm run dev
```

The app opens at http://localhost:5173 and expects the CareChat backend at http://localhost:8000
(change `BASE_URL` in `src/api.ts` if needed).

## Backend contract

| Call | Request | Response |
|---|---|---|
| `POST /upload` | multipart form, field `file` | `{ "filename": string, "extracted_text": string }` |
| `POST /chat` | `{ "question": string }` | `{ "answer": string }` |
| `POST /reset` | none | any |

## Build

```
npm run build
```
