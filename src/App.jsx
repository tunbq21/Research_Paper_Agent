import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [collectionName, setCollectionName] = useState(null)
  const [fileName, setFileName] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [isTyping, setIsTyping] = useState(false)

  const chatEndRef = useRef(null)

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (!res.ok) throw new Error('Upload failed')
      
      const data = await res.json()
      setCollectionName(data.collection_name)
      setFileName(data.filename)
      setMessages([]) // Reset chat for new document
    } catch (error) {
      console.error(error)
      alert('Error uploading document.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleAsk = async (e) => {
    e.preventDefault()
    if (!question.trim() || !collectionName || isTyping) return

    const currentQuestion = question
    setQuestion('')
    
    // Add user message to UI immediately
    const newMessages = [...messages, { role: 'user', content: currentQuestion }]
    setMessages(newMessages)
    setIsTyping(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          collection_name: collectionName,
          question: currentQuestion,
          history: messages // Send previous history for context
        }),
      })

      if (!res.ok) throw new Error('Chat request failed')
      
      const data = await res.json()
      
      // Update with assistant's answer and citations
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: data.answer, 
          citations: data.citations 
        }
      ])
    } catch (error) {
      console.error(error)
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: 'An error occurred while analyzing the document.' }
      ])
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="app-container">
      
      {/* Left Pane: Document Context */}
      <aside className="context-pane">
        <h1 className="context-header">Research Desk</h1>
        
        {!collectionName ? (
          <div className="upload-area">
            <label className="status-label">Select Document</label>
            <input 
              type="file" 
              accept="application/pdf" 
              onChange={handleFileChange}
              disabled={isUploading}
            />
            <button 
              className="btn-primary" 
              onClick={handleUpload}
              disabled={!file || isUploading}
            >
              {isUploading ? 'Indexing...' : 'Analyze PDF'}
            </button>
          </div>
        ) : (
          <div className="status-indicator">
            <span className="status-label">Active Document</span>
            <div className="doc-name">{fileName}</div>
            
            <button 
              style={{ marginTop: '2rem', background: 'transparent', border: '1px solid var(--color-border)', color: 'var(--color-text-main)' }}
              className="btn-primary"
              onClick={() => {
                setCollectionName(null)
                setFile(null)
                setMessages([])
              }}
            >
              Load New Document
            </button>
          </div>
        )}
      </aside>

      {/* Right Pane: Analysis Chat */}
      <main className="analysis-pane">
        <div className="chat-history">
          {messages.length === 0 && !isTyping && collectionName && (
            <div className="message assistant">
              <div className="message-label">System Ready</div>
              <div className="message-content">
                The document has been successfully indexed. You may now ask questions regarding its methodology, datasets, findings, or limitations.
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-label">
                {msg.role === 'user' ? 'Query' : 'Analysis'}
              </div>
              <div className="message-content">
                {msg.content}
                
                {/* Render Citations if they exist */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="citation-block">
                    <span className="message-label" style={{display: 'inline-block', marginRight: '1rem'}}>Sources:</span>
                    {msg.citations.map((cit, cIdx) => (
                      <span key={cIdx} className="citation-ref">{cit}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="message assistant">
              <div className="message-label">Analysis</div>
              <div className="loading-text">Synthesizing information...</div>
            </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

        <div className="input-area">
          <form className="input-wrapper" onSubmit={handleAsk}>
            <input 
              type="text" 
              className="chat-input"
              placeholder={collectionName ? "Inquire about the document..." : "Upload a document to begin"}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={!collectionName || isTyping}
            />
            <button 
              type="submit" 
              className="btn-send"
              disabled={!question.trim() || !collectionName || isTyping}
            >
              Ask
            </button>
          </form>
        </div>
      </main>

    </div>
  )
}

export default App
