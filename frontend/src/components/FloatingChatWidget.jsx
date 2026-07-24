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

  // Sync bookings on drawer close
  const isInitialMount = useRef(true);
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    if (!isOpen) {
      window.dispatchEvent(new CustomEvent("booking-updated"));
    }
  }, [isOpen]);

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

      // Only fire booking-updated event if a booking was actually created or cancelled by the tool
      if (response.data && response.data.booking_updated) {
        window.dispatchEvent(new CustomEvent("booking-updated"));
      }
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

  // Extract 100% clickable options/chips for EVERY step
  function getQuickReplyOptions(text) {
    if (!text) return [];
    const fullLower = text.toLowerCase();
    
    // Extract the final conversational question/line to check context keywords
    const lines = text.split("\n").map(l => l.trim()).filter(Boolean);
    const lastLine = lines.length > 0 ? lines[lines.length - 1] : "";
    const lower = lastLine.toLowerCase();

    // 0. Stop displaying options if task is successfully complete
    if (
      fullLower.includes("booking confirmed") ||
      fullLower.includes("successfully created") ||
      fullLower.includes("trip has been booked") ||
      fullLower.includes("successfully cancelled") ||
      fullLower.includes("cancellation has been confirmed") ||
      fullLower.includes("booking has been cancelled") ||
      fullLower.includes("cancelled successfully") ||
      fullLower.includes("here is the weather forecast") ||
      (fullLower.includes("booking id") && (fullLower.includes("created") || fullLower.includes("success") || fullLower.includes("confirm")))
    ) {
      return [];
    }

    const options = [];

    // 1. Hotel selection (highest priority if hotel is mentioned or listed)
    if (fullLower.includes("which hotel") || fullLower.includes("hotel preference") || fullLower.includes("select a hotel") || text.includes("Price/night") || text.includes("Rating:") || text.includes("Hotel ID:")) {
      const listLineRegex = /^\s*(?:\d+\.|\*|-)\s+\*\*(.*?)\*\*/gm;
      let listMatch;
      while ((listMatch = listLineRegex.exec(text)) !== null) {
        const label = listMatch[1].trim();
        const l = label.toLowerCase();
        if (label && !l.includes("travel dates") && !l.includes("hotel preference") && label.length < 45) {
          options.push({ label: `Book ${label}`, value: `Book ${label}` });
        }
      }
      if (options.length === 0) {
        const matches = text.matchAll(/\*\*(.*?)\*\*/g);
        for (const m of matches) {
          const name = m[1].trim();
          const l = name.toLowerCase();
          if (name && !l.includes("hotel id") && !l.includes("available hotels") && !l.includes("rating") && name.length < 45) {
            options.push({ label: `Book ${name}`, value: `Book ${name}` });
          }
        }
      }
      if (options.length > 0) return options.slice(0, 6);
    }

    // 2. Action Confirmation
    if (lower.includes("confirm") || lower.includes("proceed") || lower.includes("ready to book") || lower.includes("shall i proceed")) {
      return [
        { label: "Confirm and Book", value: "Yes, confirm and proceed with booking" },
        { label: "Cancel Request", value: "No, cancel this request" }
      ];
    }

    // 3. Cancellation Confirm/Keep
    if (lower.includes("confirm cancellation") || lower.includes("keep booking")) {
      return [
        { label: "Confirm Cancellation", value: "Yes, confirm cancellation" },
        { label: "Keep Booking", value: "No, keep booking" }
      ];
    }

    // 4. Active trips list for cancellation
    if (fullLower.includes("booking id") || fullLower.includes("cancel")) {
      const tripRegex = /Booking ID:\s*([a-f0-9]+)\s*\|\s*Destination:\s*([A-Za-z\s]+)/gi;
      let match;
      while ((match = tripRegex.exec(text)) !== null) {
        const id = match[1].trim();
        const dest = match[2].trim();
        options.push({
          label: `Cancel ${dest} Trip`,
          value: `Cancel booking ${id}`
        });
      }
      if (options.length > 0) return options.slice(0, 6);
    }

    // 5. Passport Expiry
    if (lower.includes("passport") || lower.includes("expiry") || lower.includes("valid until")) {
      const dates = ["2028-12-31", "2030-05-15", "2032-08-20"];
      return dates.map(d => ({ label: d, value: d }));
    }

    // 6. Dates / Check-in
    if (lower.includes("check-in") || lower.includes("check-out") || lower.includes("dates") || lower.includes("when are you")) {
      const dates = [
        "2026-08-10 to 2026-08-15",
        "2026-09-12 to 2026-09-15",
        "2026-10-10 to 2026-10-15",
        "2026-12-20 to 2026-12-25"
      ];
      return dates.map(d => ({ label: d, value: d }));
    }

    // 7. Destination
    if (lower.includes("destination") || lower.includes("where would you like") || lower.includes("which city") || lower.includes("travel to") || lower.includes("where to")) {
      const dests = ["Udaipur", "Goa", "Bali", "Paris", "Tokyo", "Manali", "Jaipur", "London"];
      return dests.map(d => ({ label: d, value: d }));
    }

    // 8. General Starter fallback
    if (lower.includes("hello") || lower.includes("welcome") || lower.includes("assist") || lower.includes("help")) {
      return [
        { label: "Book a trip", value: "Book a trip" },
        { label: "Cancel an active trip", value: "Cancel an active trip" },
        { label: "Check my trip weather", value: "Check my trip weather" }
      ];
    }

    return [];
  }

  const defaultStarterOptions = [
    "Book a trip",
    "Check weather for my trip",
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
                <span className="text-[10px] text-blue-100">Your Travel Genie</span>
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
                <p className="text-sm font-bold text-gray-800">Journie Interactive Agent</p>
                <p className="text-xs text-gray-500 mt-1 mb-4">Click any option below to book, cancel, or check weather step-by-step.</p>
                
                {/* Default Starter Options */}
                <div className="w-full space-y-2">
                  <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider text-left px-1">Select an option to start:</p>
                  <div className="flex flex-col gap-1.5 w-full">
                    {defaultStarterOptions.map((opt, idx) => (
                      <button
                        key={idx}
                        onClick={() => sendMessage(opt)}
                        className="w-full text-left text-xs bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-300 text-gray-700 hover:text-blue-600 font-semibold px-3 py-2.5 rounded-xl transition-all flex items-center justify-between shadow-xs cursor-pointer group"
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

                    {/* Render 100% Clickable Option Chips */}
                    {isLastAssistant && options.length > 0 && (
                      <div className="mt-2.5 flex flex-wrap gap-1.5 max-w-[92%] pl-1">
                        {options.map((opt, optIdx) => (
                          <button
                            key={optIdx}
                            onClick={() => sendMessage(opt.value)}
                            className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold px-3 py-1.5 rounded-full border border-blue-200 transition-all hover:scale-102 cursor-pointer shadow-2xs flex items-center gap-1"
                          >
                            <span>{opt.label}</span>
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
              placeholder="Click an option above or type..."
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
