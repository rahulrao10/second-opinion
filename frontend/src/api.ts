import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await axios.post(`${BASE_URL}/upload`, formData);
  return res.data as { filename: string; extracted_text: string };
}

export async function askQuestion(question: string) {
  const res = await axios.post(`${BASE_URL}/chat`, { question });
  return res.data as { answer: string };
}

export async function resetSession() {
  await axios.post(`${BASE_URL}/reset`);
}