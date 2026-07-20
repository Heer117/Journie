import { useState, useEffect, useRef } from "react";
import { MessageSquare, X, Send, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import ReactMarkdown from "react-markdown";

function FloatingChatWidget() {
  const { isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [bookings, setBookings] = useState([]);
  const [selectedBookingId, setSelectedBookingId] = useState("");
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom of messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  // Fetch bookings when widget is open and user is authenticated
  useEffect(() => {
    if (isOpen && isAuthenticated) {
      apiClient
        .get("/bookings/")
        .then((response) => {
          setBookings(response.data);
          // If the currently selected booking is no longer in the list, reset it
          const bookingIds = response.data.map((b) => b.id);
          if (selectedBookingId && !bookingIds.includes(selectedBookingId)) {
            setSelectedBookingId("");
          }
        })
        .catch((error) => {
          console.error("Error fetching bookings for chat dropdown:", error);
        });
    }
  }, [isOpen, isAuthenticated]);

  // Hide the widget completely if user is not logged in
  if (!isAuthenticated) {
    return null;
  }

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await apiClient.post("/chat/", {
        message: userMessage.content,
        booking_id: selectedBookingId || null,
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
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-2xl border border-gray-200 shadow-2xl flex flex-col overflow-hidden z-50 animate-in fade-in slide-in-from-bottom-5 duration-250">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-blue-100" />
              <div>
                <h3 className="font-bold text-sm leading-none">Journie Assistant</h3>
                <span className="text-[10px] text-blue-100">Live booking support</span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/80 hover:text-white transition-colors"
              aria-label="Close assistant"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Booking Context Dropdown */}
          {bookings.length > 0 && (
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between gap-2 flex-shrink-0">
              <label htmlFor="booking-context-select" className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Trip Context:
              </label>
              <select
                id="booking-context-select"
                value={selectedBookingId}
                onChange={(e) => setSelectedBookingId(e.target.value)}
                className="text-xs bg-white border border-gray-300 rounded-lg px-2 py-1 text-gray-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 max-w-[220px] truncate"
              >
                <option value="">General Support (None)</option>
                {bookings.map((booking) => (
                  <option key={booking.id} value={booking.id}>
                    {booking.destination} - {booking.hotel_name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-500">
                <MessageSquare className="w-10 h-10 text-gray-300 mb-2" />
                <p className="text-sm font-semibold">Welcome to Journie Chat</p>
                <p className="text-xs text-gray-400 mt-1">Ask questions about bookings, flights, visa rules, or destination guidelines.</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
                >
                  <span className="text-[10px] text-gray-400 mb-0.5 px-1">
                    {msg.role === "user" ? "You" : "Journie"}
                  </span>
                  <div
                    className={`p-3 rounded-2xl text-sm leading-relaxed max-w-[85%] ${
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
                          h1: ({ node, ...props }) => <h1 style={{ fontSize: '1.2rem', fontWeight: 'bold', marginTop: '0.75rem', marginBottom: '0.25rem', display: 'block' }} {...props} />,
                          h2: ({ node, ...props }) => <h2 style={{ fontSize: '1.05rem', fontWeight: 'bold', marginTop: '0.6rem', marginBottom: '0.2rem', display: 'block' }} {...props} />,
                          h3: ({ node, ...props }) => <h3 style={{ fontSize: '0.95rem', fontWeight: 'bold', marginTop: '0.5rem', marginBottom: '0.15rem', display: 'block' }} {...props} />,
                          p: ({ node, ...props }) => <p style={{ marginBottom: '0.5rem', display: 'block' }} {...props} />,
                          ul: ({ node, ...props }) => <ul style={{ listStyleType: 'disc', paddingLeft: '1.25rem', marginBottom: '0.5rem', display: 'block' }} {...props} />,
                          ol: ({ node, ...props }) => <ol style={{ listStyleType: 'decimal', paddingLeft: '1.25rem', marginBottom: '0.5rem', display: 'block' }} {...props} />,
                          li: ({ node, ...props }) => <li style={{ marginBottom: '0.25rem', display: 'list-item' }} {...props} />,
                          strong: ({ node, ...props }) => <strong style={{ fontWeight: 'bold', color: '#111827' }} {...props} />,
                          em: ({ node, ...props }) => <em style={{ fontStyle: 'italic' }} {...props} />,
                          a: ({ node, ...props }) => <a style={{ color: '#2563eb', textDecoration: 'underline', wordBreak: 'break-all' }} target="_blank" rel="noopener noreferrer" {...props} />
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    )}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex flex-col items-start">
                <span className="text-[10px] text-gray-400 mb-0.5 px-1">Journie</span>
                <div className="bg-white border border-gray-200 text-gray-450 rounded-2xl rounded-tl-none p-3 shadow-xs text-xs flex items-center gap-1">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-200"></div>
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
              placeholder="Ask Journie about your trip..."
            />
            <button
              onClick={sendMessage}
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
