import { useState } from 'react';
import { useTheme } from './hooks/useTheme';
import { uploadDocument, askQuestion, resetSession, type ChatMessage } from './api';
import './App.css';

export default function App() {
  const { isDark, toggle } = useTheme();
  const [docName, setDocName] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await uploadDocument(file);
      setDocName(res.filename);
      setExtractedText(res.extracted_text);
      setMessages([]);
    } catch (err) {
      alert('Failed to read document.');
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async (question: string) => {
    if (!question.trim() || !docName) return;
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setInput('');
    setLoading(true);
    try {
      const res = await askQuestion(question);
      setMessages(prev => [...prev, { role: 'assistant', content: res.answer }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    await resetSession();
    setDocName(null);
    setExtractedText('');
    setMessages([]);
  };

  const suggestions = [
    'Summarize this report',
    'What values are outside the normal range?',
    'Explain this in very simple terms',
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="wordmark">Second <span>Opinion</span></div>
        <div className="badge">● Offline · private to this device</div>

        <div className="section-label">Upload a document</div>
        <label className="upload-box">
          {uploading ? 'Reading…' : 'Click or drop a file'}
          <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileUpload} hidden />
        </label>

        {docName && (
          <>
            <div className="section-label">Current document</div>
            <div className="doc-chip">📄 {docName}</div>
            <details className="extracted-box">
              <summary>View extracted text</summary>
              <pre>{extractedText}</pre>
            </details>
            <button className="reset-btn" onClick={handleReset}>Clear & start over</button>
          </>
        )}

        <button className="theme-toggle" onClick={toggle}>
          {isDark ? '☀ Light mode' : '🌙 Dark mode'}
        </button>
      </aside>

      <main className="chat-main">
        <div className="disclaimer">
          This explains what your report says — it does not diagnose or recommend treatment. Always confirm anything important with your doctor.
        </div>

        {!docName && (
          <div className="hero">
            <h1>What's on your report?</h1>
            <p>Upload a lab report or prescription from the sidebar to get started.</p>
          </div>
        )}

        {docName && messages.length === 0 && (
          <>
            <h2 className="hero-ready">Ready — ask about {docName}</h2>
            <div className="suggestions">
              {suggestions.map(s => (
                <button key={s} className="chip" onClick={() => handleAsk(s)}>{s}</button>
              ))}
            </div>
          </>
        )}

        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>{m.content}</div>
          ))}
          {loading && <div className="bubble assistant loading">Thinking…</div>}
        </div>

        <div className="input-bar">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAsk(input)}
            placeholder={docName ? 'Ask about your report…' : 'Upload a document to start chatting'}
            disabled={!docName}
          />
          <button onClick={() => handleAsk(input)} disabled={!docName || loading}>➤</button>
        </div>
      </main>
    </div>
  );
}