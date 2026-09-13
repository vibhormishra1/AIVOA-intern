import { useState, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { chatComplaint } from '../../api/complaintApi';
import { updateFields } from '../../store/slices/complaintSlice';
import { Bot, User, Paperclip, Send } from 'lucide-react';

export default function AIIntakePanel({ complaintId, onFile, progress, message, metadata, missing }) {
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: 'Ready to process new complaints. You can paste the raw email from the customer, or upload a PDF of the complaint report. I will extract the data and run the initial risk assessment.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();
  const dispatch = useDispatch();

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    const msg = inputValue;
    setInputValue('');
    setChatHistory(prev => [...prev, { role: 'user', content: msg }]);

    if (!complaintId) {
      // If no complaint saved yet, trigger extraction
      onFile(new File([msg], "pasted.txt", { type: "text/plain" }));
      return;
    }

    setLoading(true);
    try {
      const r = await chatComplaint(complaintId, msg);
      setChatHistory(prev => [...prev, { role: 'assistant', content: r.data.response }]);
      if (r.data.updated_fields && Object.keys(r.data.updated_fields).length > 0) {
        dispatch(updateFields(r.data.updated_fields));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setChatHistory(prev => [...prev, { role: 'user', content: `Uploaded file: ${file.name}` }]);
      onFile(file);
    }
  };

  return (
    <aside className="copilot-panel">
      <header className="copilot-header">
        <div>
          <h2><Bot size={20} color="var(--primary)" /> AIVOA Copilot</h2>
          <p>Drop complaint files or paste text below.</p>
        </div>
        <div className="status-dot"></div>
      </header>

      <div className="chat-history">
        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`chat-msg ${msg.role}`}>
            <div className="avatar">
              {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
            </div>
            <div className="bubble">
              <p>{msg.content}</p>
            </div>
          </div>
        ))}
        {progress > 0 && progress < 100 && (
          <div className="chat-msg assistant">
            <div className="avatar"><Bot size={18} /></div>
            <div className="bubble">
              <p>{message || 'Extracting data...'}</p>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-wrapper">
        <div className="chat-input-box">
          <input 
            type="file" 
            ref={fileInputRef} 
            hidden 
            accept=".txt,.eml,.pdf,.docx" 
            onChange={handleFileUpload} 
          />
          <div className="attach-btn" onClick={() => fileInputRef.current.click()}>
            <Paperclip size={20} />
          </div>
          <input 
            value={inputValue} 
            onChange={e => setInputValue(e.target.value)} 
            placeholder="Type a message or paste a complaint..." 
            onKeyDown={e => e.key === 'Enter' && handleSend()}
          />
          <button onClick={handleSend} disabled={loading}>
            <Send size={16} />
          </button>
        </div>
        <div style={{ textAlign: 'center', marginTop: '10px', fontSize: '10px', color: '#94a3b8', letterSpacing: '1px' }}>
          POWERED BY LANGGRAPH
        </div>
      </div>
    </aside>
  );
}
