import { useState, useRef, useEffect, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { streamAnswer } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import CitationCard from "../components/CitationCard";

interface Citation {
  document_id: string;
  document_title: string;
  excerpt: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  isStreaming?: boolean;
}

export default function ChatPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending || !token) return;

    const question = input.trim();
    setInput("");
    setIsSending(true);

    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: "", isStreaming: true },
    ]);

    try {
      for await (const event of streamAnswer(question, token)) {
        if (event.type === "token" && event.content) {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            updated[updated.length - 1] = {
              ...last,
              content: last.content + event.content,
            };
            return updated;
          });
        } else if (event.type === "done") {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            updated[updated.length - 1] = {
              ...last,
              citations: event.citations as Citation[],
              isStreaming: false,
            };
            return updated;
          });
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Something went wrong while streaming the response. Please try again.",
          isStreaming: false,
        };
        return updated;
      });
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <div className="border-b border-slate-200 bg-white px-4 py-3 flex items-center justify-between">
        <h1 className="font-semibold text-slate-900">Knowledge Assistant Chat</h1>
        <div className="flex gap-4 text-sm">
          <Link to="/documents" className="text-slate-500 hover:underline">
            Documents
          </Link>
          <Link to="/" className="text-slate-500 hover:underline">
            Home
          </Link>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {messages.length === 0 && (
            <p className="text-slate-400 text-sm text-center mt-20">
              Ask a question about your uploaded documents to get started.
            </p>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={`max-w-lg rounded-xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-slate-900 text-white"
                    : "bg-white border border-slate-200 text-slate-800"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">
                  {msg.content}
                  {msg.isStreaming && <span className="animate-pulse">▍</span>}
                </p>

                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs font-medium text-slate-400">Sources</p>
                    {msg.citations.map((c) => (
                      <CitationCard key={c.document_id} citation={c} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={scrollRef} />
        </div>
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-white px-4 py-4">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isSending}
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isSending || !input.trim()}
            className="bg-slate-900 text-white rounded-lg px-5 py-2.5 text-sm font-medium hover:bg-slate-800 transition disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}