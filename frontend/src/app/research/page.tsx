"use client";

import { useState, useEffect, useRef } from "react";
import { Search, History, Clock, Settings, Plus, Star, Send, Paperclip, AlertCircle, FileText } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { MavenAPI } from "@/lib/api";
import { CurrencyCore } from "@/components/ui/CurrencyCore";
import { RecommendationCard } from "@/components/ui/RecommendationCard";
import Link from "next/link";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content?: string;
  isThinking?: boolean;
  stage?: string;
  report?: any;
  error?: string;
};

export default function ResearchWorkspace() {
  const [query, setQuery] = useState("");
  const [explainability, setExplainability] = useState("Intermediate");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [reportId, setReportId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    // Initialize session ID from storage or create new
    let storedSession = typeof window !== "undefined" ? sessionStorage.getItem("maven_session_id") : null;
    if (!storedSession) {
      storedSession = Math.random().toString(36).substring(2, 15);
      sessionStorage.setItem("maven_session_id", storedSession);
    }
    setSessionId(storedSession);

    const storedChat = sessionStorage.getItem(`maven_chat_${storedSession}`);
    if (storedChat) {
      try {
        setMessages(JSON.parse(storedChat));
      } catch (e) {
        console.error("Failed to parse chat history");
      }
    }

    // Attempt to load the latest report for this session
    const loadLatestReport = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/report/latest?sessionId=${storedSession}`);
        if (response.ok) {
          const data = await response.json();
          if (data && data.data) {
            setReportId(data.data.reportId);
            if (!storedChat) {
              setMessages([
                {
                  id: "restored-report",
                  role: "assistant",
                  report: { reportId: data.data.reportId },
                }
              ]);
            }
          }
        }
      } catch (err) {
        console.error("Failed to load latest report", err);
      }
    };
    
    loadLatestReport();
  }, []);

  useEffect(() => {
    if (sessionId && messages.length > 0) {
      sessionStorage.setItem(`maven_chat_${sessionId}`, JSON.stringify(messages));
    }
  }, [messages, sessionId]);

  const handleResearch = async () => {
    if (!query.trim() || isProcessing) return;

    const userMessage: ChatMessage = { id: Date.now().toString(), role: "user", content: query };
    const assistantId = (Date.now() + 1).toString();
    const assistantMessage: ChatMessage = { 
      id: assistantId, 
      role: "assistant", 
      isThinking: true,
      stage: "Initializing..."
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setQuery("");
    setIsProcessing(true);

    const updateAssistantMsg = (updates: Partial<ChatMessage>) => {
      setMessages(prev => prev.map(m => m.id === assistantId ? { ...m, ...updates } : m));
    };

    // Keep track of current report/context for follow-ups
    const history = messages.filter(m => m.content).map(m => ({ role: m.role, content: m.content }));

    await MavenAPI.chatStream(
      query,
      sessionId,
      reportId,
      history,
      null, // currentCompany could be extracted, omit for now
      explainability,
      {
        onStage: (stage, status, message) => {
          updateAssistantMsg({ stage: stage.replace(/_/g, " ").toUpperCase() });
        },
        onError: (stage, error) => {
          updateAssistantMsg({
            isThinking: false,
            stage: undefined,
            error: error
          });
          setIsProcessing(false);
        },
        onCompleted: (newReportId, reportData, content) => {
          if (newReportId) {
            setReportId(newReportId);
          }
          
          const hasReport = reportData && Object.keys(reportData).length > 0;
          
          updateAssistantMsg({
            isThinking: false,
            stage: undefined,
            report: hasReport ? { reportId: newReportId || reportData.reportId } : undefined,
            content: content
          });
          setIsProcessing(false);
        }
      }
    );
  };

  const handleNewResearch = () => {
    setMessages([]);
    setReportId(null);
    setQuery("");
    const newSession = Math.random().toString(36).substring(2, 15);
    sessionStorage.setItem("maven_session_id", newSession);
    sessionStorage.removeItem(`maven_chat_${newSession}`);
    setSessionId(newSession);
  };

  return (
    <div className="flex h-screen bg-[var(--color-maven-bg)] text-white overflow-hidden">
      {/* LEFT SIDEBAR */}
      <aside className="w-64 border-r border-white/5 bg-[#0a0808] hidden md:flex flex-col">
        <div className="p-6">
          <Link href="/" className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            Maven
          </Link>
        </div>
        
        <div className="px-4 mb-6">
          <button onClick={handleNewResearch} className="w-full flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors border border-white/5">
            <Plus size={16} /> New Research
          </button>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          <div className="text-xs font-semibold text-[var(--color-maven-gray-500)] uppercase tracking-wider mb-3 px-2 mt-4">Workspace</div>
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm text-[var(--color-maven-gray-400)] hover:text-white hover:bg-white/5 rounded-md transition-colors">
            <Clock size={16} /> Recent Research <span className="ml-auto text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-[var(--color-maven-gray-500)]">Soon</span>
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm text-[var(--color-maven-gray-400)] hover:text-white hover:bg-white/5 rounded-md transition-colors">
            <History size={16} /> History <span className="ml-auto text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-[var(--color-maven-gray-500)]">Soon</span>
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm text-[var(--color-maven-gray-400)] hover:text-white hover:bg-white/5 rounded-md transition-colors">
            <Star size={16} /> Watchlist <span className="ml-auto text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-[var(--color-maven-gray-500)]">Soon</span>
          </a>
        </nav>

        <div className="p-4 border-t border-white/5">
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm text-[var(--color-maven-gray-400)] hover:text-white hover:bg-white/5 rounded-md transition-colors">
            <Settings size={16} /> Settings
          </a>
        </div>
      </aside>

      {/* MAIN CHAT AREA */}
      <main className="flex-1 flex flex-col relative">
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-[760px] mx-auto flex flex-col gap-8 pb-40">
            
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center text-center mt-32 opacity-50">
                <CurrencyCore size="lg" />
                <h2 className="text-2xl font-medium mt-12 text-white">How can Maven assist you?</h2>
                <p className="text-[var(--color-maven-gray-400)] mt-3 text-sm">Request a deep-dive analysis on any public company.</p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-4 duration-500`}>
                {msg.role === "user" ? (
                  <div className="bg-[#1f1a1a] text-white px-5 py-3.5 rounded-2xl max-w-[85%] border border-white/5 shadow-sm text-[15px] leading-relaxed">
                    {msg.content}
                  </div>
                ) : (
                  <div className="w-full flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-[var(--color-maven-bg)] border border-[var(--color-maven-primary)]/30 flex items-center justify-center shrink-0 mt-1 shadow-[0_0_10px_rgba(209,58,74,0.15)]">
                      <span className="text-[10px] font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-[var(--color-maven-gray-400)]">M</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <AnimatePresence mode="wait">
                        {msg.isThinking ? (
                          <motion.div 
                            initial={{ opacity: 0 }} 
                            animate={{ opacity: 1 }} 
                            exit={{ opacity: 0 }}
                            className="flex flex-col items-center justify-center py-12"
                          >
                            <CurrencyCore size="md" />
                            <motion.p 
                              key={msg.stage}
                              initial={{ opacity: 0, y: 5 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="mt-8 text-sm text-[var(--color-maven-gray-400)] tracking-wide font-medium uppercase"
                            >
                              {msg.stage}
                            </motion.p>
                          </motion.div>
                        ) : msg.error ? (
                          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start gap-3">
                            <AlertCircle size={18} className="shrink-0 mt-0.5" />
                            <p>{msg.error}</p>
                          </div>
                        ) : (
                          <div className="flex flex-col gap-4">
                            {msg.content && (
                              <div className="text-[15px] leading-relaxed text-gray-200 whitespace-pre-wrap">
                                {msg.content}
                              </div>
                            )}
                            {msg.report && msg.report.reportId && (
                              <div className="mt-2 flex">
                                <Link 
                                  href={`/research/${msg.report.reportId}`}
                                  className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/10 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-2"
                                >
                                  <FileText size={14} /> View Full Report
                                </Link>
                              </div>
                            )}
                          </div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* BOTTOM INPUT */}
        <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[var(--color-maven-bg)] via-[var(--color-maven-bg)] to-transparent pt-10 pb-6 px-4 md:px-8">
          <div className="max-w-[760px] mx-auto">
            <div className="bg-[#110e0e] border border-white/10 rounded-2xl p-2 shadow-[0_0_30px_rgba(0,0,0,0.5)] focus-within:border-[var(--color-maven-gray-500)] transition-colors">
              <textarea 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleResearch();
                  }
                }}
                placeholder="Ask Maven to research any public company..."
                className="w-full bg-transparent text-white px-3 py-2 text-[15px] outline-none resize-none max-h-32 min-h-[44px] placeholder:text-[var(--color-maven-gray-500)]"
                rows={1}
                disabled={isProcessing}
              />
              <div className="flex items-center justify-between px-2 pt-2 mt-1 border-t border-white/5">
                <div className="flex items-center gap-3">
                  <button className="text-[var(--color-maven-gray-500)] hover:text-white transition-colors p-1" title="Attach file (future)">
                    <Paperclip size={18} />
                  </button>
                </div>
                <button 
                  onClick={handleResearch}
                  disabled={!query.trim() || isProcessing}
                  className="p-1.5 bg-white text-black rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:bg-white/10 disabled:text-white/30 transition-colors"
                >
                  <Send size={16} className="ml-0.5" />
                </button>
              </div>
            </div>
            <p className="text-center text-[11px] text-[var(--color-maven-gray-500)] mt-3">
              Maven relies on deterministic logic and live data, but can still make mistakes. Verify important financial decisions.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
