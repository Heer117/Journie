import { useState, useEffect, useRef } from "react";
import { MessageSquare, X, Send, Sparkles, ChevronRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import ReactMarkdown from "react-markdown";

function FloatingChatWidget() {
  const { isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom of messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, loading]);

  if (!isAuthenticated) {
    return null;
  }

  async function sendMessage(textToSend) {
    const text = textToSend || input;
    if (!text || !text.trim()) return;

    const userMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await apiClient.post("/chat/", {
        message: userMessage.content,
      });

      const assistantMessage = { role: "assistant", content: response.data.reply };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat request failed:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong reaching the server." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  // Extract interactive quick options/chips from assistant message text
  function getQuickReplyOptions(text) {
    if (!text) return [];
    const options = [];

    // Extract bolded items from numbered or bulleted lists (e.g. 1. **The Oberoi Udaivilas**: ...)
    const listLineRegex = /^\s*(?:\d+\.|\*|-)\s+\*\*(.*?)\*\*/gm;
    let listMatch;
    while ((listMatch = listLineRegex.exec(text)) !== null) {
      const label = listMatch[1].replace(/Available hotels in.*/i, "").trim();
      const lower = label.toLowerCase();
      if (
        label &&
        !lower.includes("travel dates") &&
        !lower.includes("hotel preference") &&
        !lower.includes("hotel options") &&
        !lower.includes("udaipur trip") &&
        !lower.includes("trip details") &&
        !lower.includes("destination") &&
        label.length < 45
      ) {
        if (text.toLowerCase().includes("hotel") || text.toLowerCase().includes("udaipur") || text.toLowerCase().includes("paris")) {
          options.push(`Book ${label}`);
        } else {
          options.push(label);
        }
      }
    }

    // Fallback regex for standalone bold items if no list match
    if (options.length === 0 && (text.includes("Available hotels") || text.includes("Price/night") || text.includes("Rating:") || text.includes("Hotel ID:"))) {
      const matches = text.matchAll(/\*\*(.*?)\*\*/g);
      for (const m of matches) {
        const name = m[1].replace(/Available hotels in.*/i, "").trim();
        const lower = name.toLowerCase();
        if (name && !lower.includes("hotel id") && !lower.includes("available hotels") && !lower.includes("rating") && name.length < 40) {
          options.push(`Book ${name}`);
        }
      }
    }

    // 2. Action Confirmation detector
    if (text.toLowerCase().includes("confirm") || text.toLowerCase().includes("would you like me to proceed") || text.toLowerCase().includes("proceed with this booking")) {
      options.push("Yes, confirm and proceed with booking");
      options.push("No, cancel this request");
    }

    // 3. Cancellation confirmation
    if (text.toLowerCase().includes("cancel your booking") || text.toLowerCase().includes("confirm cancellation")) {
      options.push("Yes, confirm cancellation");
      options.push("No, keep booking");
    }

    // 4. Destination selector
    if (text.toLowerCase().includes("destination") || text.toLowerCase().includes("where would you like to travel") || text.toLowerCase().includes("which city")) {
      options.push("Paris");
      options.push("Goa");
      options.push("Bali");
      options.push("Udaipur");
      options.push("Tokyo");
      options.push("London");
    }

    // Deduplicate and return top 6
    return Array.from(new Set(options)).slice(0, 6);
  }

  const defaultStarterOptions = [
    "Book a new trip",
    "What hotels are in Paris?",
    "Check my trip weather",
    "Cancel an active trip",
  ];

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-105 z-50 cursor-pointer"
        aria-label="Toggle chat assistant"
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>

      {/* Chat Drawer Overlay */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[520px] bg-white rounded-2xl border border-gray-200 shadow-2xl flex flex-col overflow-hidden z-50 animate-in fade-in slide-in-from-bottom-5 duration-250">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-blue-100" />
              <div>
                <h3 className="font-bold text-sm leading-none">Journie Assistant</h3>
                <span className="text-[10px] text-blue-100">Live booking & cancellation support</span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/80 hover:text-white transition-colors cursor-pointer"
              aria-label="Close assistant"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-4 text-gray-500">
                <MessageSquare className="w-10 h-10 text-blue-500/80 mb-2" />
                <p className="text-sm font-bold text-gray-800">Journie Travel Agent</p>
                <p className="text-xs text-gray-500 mt-1 mb-4">I can help you search hotels, book trips, check weather, or manage cancellations step-by-step.</p>
                
                {/* Default Starter MCQ Chips */}
                <div className="w-full space-y-2">
                  <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider text-left px-1">Select an option to start:</p>
                  <div className="flex flex-col gap-1.5 w-full">
                    {defaultStarterOptions.map((opt, idx) => (
                      <button
                        key={idx}
                        onClick={() => sendMessage(opt)}
                        className="w-full text-left text-xs bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-300 text-gray-700 hover:text-blue-600 font-medium px-3 py-2 rounded-xl transition-all flex items-center justify-between shadow-xs cursor-pointer group"
                      >
                        <span>{opt}</span>
                        <ChevronRight className="w-3.5 h-3.5 text-gray-400 group-hover:text-blue-600" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => {
                const options = msg.role === "assistant" ? getQuickReplyOptions(msg.content) : [];
                const isLastAssistant = msg.role === "assistant" && idx === messages.length - 1;

                return (
                  <div
                    key={idx}
                    className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
                  >
                    <span className="text-[10px] text-gray-400 mb-0.5 px-1">
                      {msg.role === "user" ? "You" : "Journie"}
                    </span>
                    <div
                      className={`p-3 rounded-2xl text-sm leading-relaxed max-w-[88%] ${
                        msg.role === "user"
                          ? "bg-blue-600 text-white rounded-tr-none shadow-sm"
                          : "bg-white border border-gray-200 text-gray-800 rounded-tl-none shadow-xs"
                      }`}
                    >
                      {msg.role === "user" ? (
                        msg.content
                      ) : (
                        <ReactMarkdown
                          components={{
                            h1: ({ node, ...props }) => <h1 style={{ fontSize: '1.1rem', fontWeight: 'bold', marginTop: '0.5rem', marginBottom: '0.25rem', display: 'block' }} {...props} />,
                            h2: ({ node, ...props }) => <h2 style={{ fontSize: '1.0rem', fontWeight: 'bold', marginTop: '0.4rem', marginBottom: '0.2rem', display: 'block' }} {...props} />,
                            h3: ({ node, ...props }) => <h3 style={{ fontSize: '0.9rem', fontWeight: 'bold', marginTop: '0.3rem', marginBottom: '0.15rem', display: 'block' }} {...props} />,
                            p: ({ node, ...props }) => <p style={{ marginBottom: '0.35rem', display: 'block' }} {...props} />,
                            ul: ({ node, ...props }) => <ul style={{ listStyleType: 'disc', paddingLeft: '1.2rem', marginBottom: '0.35rem', display: 'block' }} {...props} />,
                            ol: ({ node, ...props }) => <ol style={{ listStyleType: 'decimal', paddingLeft: '1.2rem', marginBottom: '0.35rem', display: 'block' }} {...props} />,
                            li: ({ node, ...props }) => <li style={{ marginBottom: '0.2rem', display: 'list-item' }} {...props} />,
                            strong: ({ node, ...props }) => <strong style={{ fontWeight: 'bold', color: '#111827' }} {...props} />,
                            em: ({ node, ...props }) => <em style={{ fontStyle: 'italic' }} {...props} />,
                            a: ({ node, ...props }) => <a style={{ color: '#2563eb', textDecoration: 'underline', wordBreak: 'break-all' }} target="_blank" rel="noopener noreferrer" {...props} />
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>

                    {/* Render Quick Reply Option Buttons / Chips */}
                    {isLastAssistant && options.length > 0 && (
                      <div className="mt-2.5 flex flex-wrap gap-1.5 max-w-[92%] pl-1">
                        {options.map((optText, optIdx) => (
                          <button
                            key={optIdx}
                            onClick={() => sendMessage(optText)}
                            className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold px-3 py-1.5 rounded-full border border-blue-200 transition-all hover:scale-102 cursor-pointer shadow-2xs flex items-center gap-1"
                          >
                            <span>{optText}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })
            )}
            {loading && (
              <div className="flex flex-col items-start">
                <span className="text-[10px] text-gray-400 mb-0.5 px-1">Journie</span>
                <div className="bg-white border border-gray-200 text-gray-450 rounded-2xl rounded-tl-none p-3 shadow-xs text-xs flex items-center gap-1">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-100"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-3 border-t border-gray-150 flex gap-2 items-center bg-gray-50">
            <input
              type="text"
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type message or select an option above..."
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg disabled:opacity-50 transition-colors flex items-center justify-center cursor-pointer shadow-sm"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

        </div>
      )}
    </>
  );
}

export default FloatingChatWidget;
