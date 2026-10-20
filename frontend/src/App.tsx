import { useRef, useState, type ChangeEvent, type DragEvent, type ReactNode } from 'react';
import { useTheme } from './hooks/useTheme';
import { uploadDocument, askQuestion, type ChatMessage } from './api';
import './App.css';

const suggestions = [
  { icon: '≡', text: 'Give me a clear summary' },
  { icon: '↕', text: 'What results need attention?' },
  { icon: 'Aa', text: 'Explain the medical terms' },
];

type IconName = 'shield' | 'upload' | 'file' | 'sun' | 'moon' | 'send' | 'spark' | 'check' | 'refresh' | 'arrow';

function Icon({ name }: { name: IconName }) {
  const paths: Record<IconName, ReactNode> = {
    shield: <><path d="M12 3 20 6v5c0 5.2-3.4 9-8 10-4.6-1-8-4.8-8-10V6l8-3Z"/><path d="m8.7 12 2.1 2.1 4.6-4.7"/></>,
    upload: <><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 15v4h14v-4"/></>,
    file: <><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v5h5"/><path d="M10 13h4M10 17h4"/></>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></>,
    moon: <path d="M20.4 14.4A8.6 8.6 0 0 1 9.6 3.6a8.7 8.7 0 1 0 10.8 10.8Z"/>,
    send: <><path d="m21 3-7.2 18-3.9-8.1L2 9l19-6Z"/><path d="M10 13 21 3"/></>,
    spark: <><path d="m12 3 1.2 5.8L19 10l-5.8 1.2L12 17l-1.2-5.8L5 10l5.8-1.2L12 3Z"/><path d="m19 16 .6 2.4L22 19l-2.4.6L19 22l-.6-2.4L19 16Z"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    refresh: <><path d="M20 11a8.1 8.1 0 0 0-14.7-4L3 10"/><path d="M3 5v5h5"/><path d="M4 13a8.1 8.1 0 0 0 14.7 4L21 14"/><path d="M21 19v-5h-5"/></>,
    arrow: <path d="M5 12h13M13 6l6 6-6 6"/>,
  };
  return <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

export default function App() {
  const { isDark, toggle } = useTheme();
  const inputRef = useRef<HTMLInputElement>(null);
  const [docName, setDocName] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState('');
  const [showText, setShowText] = useState(false);

  const processFile = async (file: File) => {
    const allowed = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!allowed.includes(file.type)) { setError('Please choose a PDF, JPG, or PNG report.'); return; }
    if (file.size > 15 * 1024 * 1024) { setError('Please choose a report smaller than 15 MB.'); return; }
    setError(''); setUploading(true);
    try {
      const res = await uploadDocument(file);
      setDocName(res.filename); setExtractedText(res.extracted_text); setMessages([]); setShowText(false);
    } catch { setError('We could not read this report. Please try again.'); }
    finally { setUploading(false); }
  };

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await processFile(file);
    e.target.value = '';
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault(); setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) await processFile(file);
  };

  const handleAsk = async (question: string) => {
    if (!question.trim() || !docName || loading) return;
    setError(''); setMessages(prev => [...prev, { role: 'user', content: question.trim() }]); setInput(''); setLoading(true);
    try {
      const res = await askQuestion(question.trim());
      setMessages(prev => [...prev, { role: 'assistant', content: res.answer }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'I could not complete that request. Please check the server connection and try again.' }]);
    } finally { setLoading(false); }
  };

  const handleReset = () => {
    // Deliberately does not call the backend /reset: the backend archives the current report into
    // patient memory when the next one is uploaded, which keeps cross-report questions working.
    setDocName(null); setExtractedText(''); setMessages([]); setInput(''); setError(''); setShowText(false);
  };

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="brand">
          <div className="brand-mark"><Icon name="shield" /></div>
          <div><div className="brand-name">Care<span>Chat</span></div><div className="brand-sub">Medical report analyzer</div></div>
        </div>
        <div className="header-actions">
          <div className="secure-badge"><span /> Private workspace</div>
          <button className="theme-button" onClick={toggle} aria-label="Toggle appearance"><Icon name={isDark ? 'sun' : 'moon'} /></button>
        </div>
      </header>

      <main className="page">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow"><span className="eyebrow-dot" /> HEALTH REPORT REVIEW</span>
            <h1>Make sense of your<br /><em>medical report.</em></h1>
            <p>Upload a report to understand the results, identify information that may need attention, and ask questions in plain language.</p>
          </div>
          <div className="hero-detail">
            <div className="detail-icon"><Icon name="shield" /></div>
            <div><strong>Clear, responsible explanations</strong><span>Designed to support conversations with your healthcare professional.</span></div>
          </div>
        </section>

        <section className={`report-card ${docName ? 'report-ready' : ''} ${isDragging ? 'dragging' : ''}`} onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }} onDragLeave={() => setIsDragging(false)} onDrop={handleDrop}>
          <input ref={inputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileUpload} hidden />
          {!docName ? (
            <div className="upload-content">
              <div className="upload-symbol"><Icon name={uploading ? 'refresh' : 'upload'} /></div>
              <div className="upload-copy">
                <span className="card-label">START WITH A REPORT</span>
                <h2>{uploading ? 'Reading your report…' : 'Upload your medical report'}</h2>
                <p>{uploading ? 'Please wait while we prepare it for review.' : 'PDF, JPG or PNG · maximum 15 MB'}</p>
              </div>
              {!uploading && <button className="upload-button" onClick={() => inputRef.current?.click()}>Choose report <Icon name="arrow" /></button>}
              {uploading && <div className="progress-ring"><span /></div>}
            </div>
          ) : (
            <div className="report-content">
              <div className="report-file-icon"><Icon name="file" /></div>
              <div className="report-meta"><span className="card-label">REPORT READY</span><h2 title={docName}>{docName}</h2><p><span className="ready-dot" /> Ready for review</p></div>
              <div className="report-actions">
                <button className="text-button" onClick={() => setShowText(v => !v)}>{showText ? 'Hide report text' : 'View report text'}</button>
                <button className="outline-button" onClick={handleReset}><Icon name="refresh" /> New report</button>
              </div>
            </div>
          )}
          {error && <div className="error-message">{error}</div>}
          {docName && showText && <div className="extracted-box"><pre>{extractedText || 'No text was extracted.'}</pre></div>}
        </section>

        {!docName && <section className="value-grid">
          <div><span>01</span><strong>Understand</strong><p>Turn complex medical wording into clear explanations.</p></div>
          <div><span>02</span><strong>Explore</strong><p>Ask focused questions about the information in your report.</p></div>
          <div><span>03</span><strong>Prepare</strong><p>Use the conversation to prepare for a discussion with your doctor.</p></div>
        </section>}

        <section className={`workspace ${docName ? 'visible' : ''}`}>
          {docName && messages.length === 0 && <div className="question-start">
            <div className="section-heading"><div className="assistant-mark"><Icon name="spark" /></div><div><span className="card-label">REPORT REVIEW</span><h2>What would you like to know?</h2><p>Start with a suggested question or write your own.</p></div></div>
            <div className="suggestions">{suggestions.map(s => <button key={s.text} className="suggestion" onClick={() => handleAsk(s.text)}><span className="suggestion-icon">{s.icon}</span><span>{s.text}</span><Icon name="arrow" /></button>)}</div>
          </div>}

          <div className={`messages ${messages.length ? 'has-messages' : ''}`}>
            {messages.map((m, i) => <div key={`${m.role}-${i}`} className={`message-row ${m.role}`}>
              {m.role === 'assistant' && <div className="assistant-avatar"><Icon name="spark" /></div>}
              <div className={`bubble ${m.role}`}>{m.content}</div>
            </div>)}
            {loading && <div className="message-row assistant"><div className="assistant-avatar"><Icon name="spark" /></div><div className="bubble assistant loading"><span /><span /><span /> Reviewing…</div></div>}
          </div>

          <div className="composer-wrap">
            <div className={`input-bar ${!docName ? 'disabled' : ''}`}>
              <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAsk(input); } }} placeholder={docName ? 'Ask a question about your report…' : 'Upload a report to begin'} disabled={!docName || loading} aria-label="Question about your report" />
              <button className="send-btn" onClick={() => handleAsk(input)} disabled={!docName || loading || !input.trim()} aria-label="Send question"><Icon name="send" /></button>
            </div>
            {docName && <div className="composer-note"><span>Press Enter to send</span><span>Not a diagnosis. Discuss important results with your healthcare professional.</span></div>}
          </div>
        </section>

        <footer className="page-footer"><span><Icon name="shield" /> Your report stays within this review session.</span><span>CareChat · Health report companion</span></footer>
      </main>
    </div>
  );
}
