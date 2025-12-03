import { useState, useRef, useEffect } from "react";
import { Send, Mic } from "lucide-react";
import MessageBubble from "./components/MessageBubble";
import LoadingDots from "./components/LoadingDots";
import useSpeechRecognition from "./hooks/useSpeechRecognition";
import useSpeechSynthesis from "./hooks/useSpeechSynthesis";

const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || "http://localhost:8080/chat";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "ai", content: "Hello! I can help you analyze and visualize retail data." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const { speak } = useSpeechSynthesis();

  const { startListening } = useSpeechRecognition((transcript) => {
    setInput(transcript);
    sendMessage(transcript);
  });

  const bottomRef = useRef(null);
  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  async function sendMessage(text) {
    const content = text || input;
    if (!content.trim()) return;

    setMessages((m) => [...m, { role: "user", content }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content })
      });

      const data = await res.json();

      setMessages((m) => [...m, { role: "ai", ...data }]);

      // Auto speak AI summary
      if ((data.type === "text" || data.type === "analytics") && data.content) {
        speak(data.content);
      }
    } catch (err) {
      console.error(err);
      setMessages((m) => [
        ...m,
        {
          role: "ai",
          content: "Error connecting to the backend."
        }
      ]);
    }

    setLoading(false);
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="p-4 shadow-sm bg-gray-800 border-b border-gray-700 text-xl font-bold text-gray-100">
        Retail Analytics Assistant
      </header>

      <main className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-4xl mx-auto">
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg} isUser={msg.role === "user"} />
            ))}
            {loading && <LoadingDots />}
            <div ref={bottomRef} />
        </div>
      </main>

      <footer className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="max-w-4xl mx-auto flex gap-4 items-center">
            <button onClick={startListening} className="p-3 bg-gray-700 hover:bg-gray-600 rounded-full text-gray-100 transition-colors">
              <Mic size={20} />
            </button>

            <input
              className="flex-1 p-3 border border-gray-600 bg-gray-700 text-gray-100 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about sales, profit, etc."
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />

            <button
              onClick={() => sendMessage()}
              className="p-3 bg-blue-500 hover:bg-blue-600 text-white rounded-full transition-colors disabled:opacity-50"
              disabled={!input.trim() || loading}
            >
              <Send size={20} />
            </button>
        </div>
      </footer>
    </div>
  );
}
