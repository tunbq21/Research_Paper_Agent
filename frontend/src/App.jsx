import { useState, useRef, useEffect } from 'react';
import { Upload, Send, FileText, Loader2, Sparkles, Database, Home, Settings, Search, LayoutGrid } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [file, setFile] = useState(null);
  const [collectionName, setCollectionName] = useState(null);
  const [fileName, setFileName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!res.ok) throw new Error('Upload failed');
      
      const data = await res.json();
      setCollectionName(data.collection_name);
      setFileName(data.filename);
      setMessages([]); 
    } catch (error) {
      console.error(error);
      alert('Error uploading document.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAsk = async (e) => {
    if (e) e.preventDefault();
    if (!question.trim() || !collectionName || isTyping) return;

    const currentQuestion = question;
    setQuestion('');
    
    const newMessages = [...messages, { role: 'user', content: currentQuestion }];
    setMessages(newMessages);
    setIsTyping(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          collection_name: collectionName,
          question: currentQuestion,
          history: messages
        }),
      });

      if (!res.ok) throw new Error('Chat request failed');
      
      const data = await res.json();
      
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: data.answer, citations: data.citations }
      ]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: 'An error occurred while analyzing the document.' }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden text-white bg-black relative font-sans">
      {/* Deep atmospheric background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_#1a1a2e_0%,_#000000_100%)]"></div>
        <div className="absolute top-0 right-0 w-[40vw] h-[40vh] bg-blue-900/20 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-0 left-0 w-[60vw] h-[60vh] bg-indigo-900/10 blur-[150px] rounded-full"></div>
      </div>

      {/* Sidebar - Glass panel */}
      <aside className="w-20 md:w-64 glass-panel border-y-0 border-l-0 border-r flex flex-col justify-between py-8 px-4 z-10 transition-all duration-300 hidden sm:flex">
        <div className="flex flex-col gap-8">
          <div className="flex items-center gap-3 px-2">
            <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-black shrink-0">
              <Sparkles size={20} className="ml-0.5" />
            </div>
            <div className="hidden md:block">
              <h1 className="font-bold tracking-widest text-sm text-gradient">NEOVISION</h1>
              <p className="text-[10px] text-white/40 uppercase tracking-widest">Research AI</p>
            </div>
          </div>
          
          <nav className="flex flex-col gap-2 mt-8">
            {[
              { icon: Home, label: "Dashboard", active: !collectionName },
              { icon: Database, label: "Knowledge Base", active: !!collectionName },
              { icon: LayoutGrid, label: "Modules" },
              { icon: Search, label: "Explore" }
            ].map((item, i) => (
              <button 
                key={i}
                className={`flex items-center gap-4 p-3 rounded-2xl transition-all duration-300
                  ${item.active 
                    ? 'bg-white/10 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]' 
                    : 'text-white/40 hover:bg-white/5 hover:text-white'}`}
              >
                <item.icon size={22} className="shrink-0" />
                <span className="hidden md:block text-sm font-medium tracking-wide">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <button className="flex items-center gap-4 p-3 rounded-2xl text-white/40 hover:bg-white/5 hover:text-white transition-all duration-300">
          <Settings size={22} className="shrink-0" />
          <span className="hidden md:block text-sm font-medium tracking-wide">Settings</span>
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative z-10 h-full overflow-hidden">
        
        {/* Top Navbar */}
        <header className="h-20 flex items-center justify-between px-6 sm:px-10 shrink-0">
          <div className="flex items-center gap-4 sm:hidden">
            <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-black shrink-0">
              <Sparkles size={20} />
            </div>
          </div>
          <div className="hidden sm:flex flex-col">
            <h2 className="text-xs uppercase tracking-[0.2em] text-white/40">Digital Frontier</h2>
            <p className="text-sm tracking-wide text-white/80">Research Intelligence Agent</p>
          </div>
          {collectionName && (
            <div className="glass-panel px-4 py-2 rounded-full flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-green-400 shadow-[0_0_10px_rgba(74,222,128,0.8)]"></div>
              <span className="text-xs font-medium tracking-widest text-white/80 uppercase">Linked: {fileName}</span>
              <button 
                onClick={() => {
                  setCollectionName(null);
                  setFile(null);
                  setMessages([]);
                }}
                className="ml-4 text-xs text-white/40 hover:text-white transition-colors"
              >
                Clear
              </button>
            </div>
          )}
        </header>

        <div className="flex-1 flex flex-col overflow-hidden px-6 sm:px-10 pb-6">
          
          {!collectionName ? (
            /* Upload State */
            <div className="flex-1 flex flex-col items-center justify-center max-w-4xl mx-auto w-full">
              <div className="text-center mb-16 space-y-4">
                <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-white font-sans uppercase">
                  New Digital<br />
                  <span className="text-white/30">Universe</span>
                </h1>
                <p className="text-white/40 max-w-lg mx-auto text-sm md:text-base tracking-wide leading-relaxed mt-6">
                  Step into The Digital Frontier, where boundaries between documents and virtual innovation disappear. Upload a paper to initiate the neural link.
                </p>
              </div>

              <div className="w-full max-w-xl glass-panel rounded-3xl p-1 overflow-hidden relative group transition-all duration-500 hover:shadow-[0_0_40px_rgba(255,255,255,0.05)]">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out"></div>
                <div className="border border-dashed border-white/20 rounded-[22px] p-10 flex flex-col items-center justify-center text-center bg-black/20 backdrop-blur-sm">
                  <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 group-hover:bg-white/10 transition-colors duration-500">
                    <FileText size={32} className="text-white/60" />
                  </div>
                  
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={handleFileChange}
                    accept=".pdf"
                  />
                  
                  {file ? (
                    <div className="space-y-6 w-full">
                      <div className="glass-panel p-4 rounded-xl flex items-center justify-between">
                        <span className="truncate text-sm text-white/80 tracking-wide pr-4">{file.name}</span>
                        <span className="text-xs text-white/40 shrink-0">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                      </div>
                      <button
                        onClick={handleUpload}
                        disabled={isUploading}
                        className="w-full bg-white text-black py-4 rounded-xl font-bold tracking-widest uppercase text-sm hover:bg-gray-200 transition-colors disabled:opacity-50 flex items-center justify-center gap-3 cursor-pointer"
                      >
                        {isUploading ? (
                          <>
                            <Loader2 className="animate-spin" size={18} />
                            <span>Establishing Link...</span>
                          </>
                        ) : (
                          <>
                            <Database size={18} />
                            <span>Initialize Context</span>
                          </>
                        )}
                      </button>
                    </div>
                  ) : (
                    <>
                      <h3 className="text-xl font-medium tracking-wide mb-2">Select a document</h3>
                      <p className="text-sm text-white/40 mb-8 max-w-xs">PDF format supported. Secure, local processing.</p>
                      <label
                        htmlFor="file-upload"
                        className="cursor-pointer bg-white/10 hover:bg-white/20 border border-white/10 px-8 py-3 rounded-full text-sm tracking-widest uppercase font-medium transition-all duration-300 inline-block"
                      >
                        Browse Files
                      </label>
                    </>
                  )}
                </div>
              </div>
            </div>
          ) : (
            /* Chat State */
            <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full h-full relative">
              <div className="flex-1 overflow-y-auto pr-2 sm:pr-4 custom-scrollbar flex flex-col gap-6 pb-28 pt-4">
                {messages.length === 0 && (
                  <div className="flex-1 flex flex-col items-center justify-center opacity-50">
                    <Sparkles size={48} className="mb-4 text-white/20" />
                    <p className="text-lg tracking-widest uppercase text-white/40">Link Established</p>
                    <p className="text-sm text-white/30 mt-2 text-center max-w-md">The document has been successfully indexed. Ask questions regarding methodology, datasets, findings, or limitations.</p>
                  </div>
                )}
                
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-4 duration-500`}
                  >
                    <div
                      className={`max-w-[85%] sm:max-w-[75%] rounded-3xl p-6 ${
                        msg.role === 'user'
                          ? 'bg-white text-black rounded-tr-none'
                          : 'glass-panel text-white/90 rounded-tl-none shadow-[0_4px_24px_rgba(0,0,0,0.2)]'
                      }`}
                    >
                      {msg.role === 'assistant' && (
                        <div className="flex items-center gap-2 mb-4 pb-4 border-b border-white/10">
                          <Sparkles size={14} className="text-white/40" />
                          <span className="text-[10px] uppercase tracking-[0.2em] text-white/40">Analysis Node</span>
                        </div>
                      )}
                      <div className="prose prose-sm md:prose-base prose-invert max-w-none 
                        prose-p:leading-relaxed prose-p:tracking-wide
                        prose-headings:font-sans prose-headings:tracking-tight
                        prose-a:text-blue-400
                        prose-code:bg-white/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:text-white/90
                        prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/10"
                      >
                        {msg.role === 'user' ? (
                          <div className="text-black font-medium leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                        ) : (
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="flex justify-start animate-in fade-in">
                    <div className="glass-panel rounded-3xl rounded-tl-none p-6 flex items-center gap-4">
                      <div className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce"></div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              <div className="absolute bottom-0 left-0 right-0 pt-8 pb-4 bg-gradient-to-t from-black via-black/90 to-transparent">
                <div className="glass-panel p-2 rounded-[2rem] flex items-end shadow-[0_0_40px_rgba(0,0,0,0.5)] bg-black/60 backdrop-blur-2xl mx-1">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Inquire about the document..."
                    className="flex-1 bg-transparent border-none outline-none text-white placeholder-white/30 px-6 py-4 resize-none min-h-[56px] max-h-32 overflow-y-auto text-base tracking-wide"
                    rows={1}
                  />
                  <button
                    onClick={handleAsk}
                    disabled={isTyping || !question.trim()}
                    className="m-2 w-12 h-12 flex items-center justify-center bg-white text-black rounded-full shrink-0 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:bg-white/20 disabled:text-white/40 cursor-pointer"
                  >
                    <Send size={18} className="ml-1" />
                  </button>
                </div>
                <div className="text-center mt-3">
                  <span className="text-[10px] uppercase tracking-[0.2em] text-white/30">Neovision can make mistakes. Verify critical information.</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        textarea::-webkit-scrollbar {
          width: 6px;
        }
        textarea::-webkit-scrollbar-track {
          background: transparent;
        }
        textarea::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        textarea::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}} />
    </div>
  );
}

export default App;
