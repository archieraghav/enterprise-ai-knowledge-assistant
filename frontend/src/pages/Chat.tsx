import { useState, useRef, useEffect, type FormEvent } from "react";
import { streamAnswer } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import Header from "../components/Header";
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
            updated[updated.length - 1] = { ...last, content: last.content + event.content };
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
    <div className="min-h-screen flex flex-col bg-neutral-50 dark:bg-neutral-950">
      <Header />

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {messages.length === 0 && (
            <p className="text-neutral-400 dark:text-neutral-600 text-sm text-center mt-20">
              Ask a question about your uploaded documents to get started.
            </p>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={`max-w-[85%] sm:max-w-lg rounded-xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-neutral-900 dark:bg-brand-600 text-white"
                    : "card text-neutral-800 dark:text-neutral-100"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">
                  {msg.content}
                  {msg.isStreaming && <span className="animate-pulse">▍</span>}
                </p>

                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs font-medium text-neutral-400 dark:text-neutral-500">Sources</p>
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

      <form onSubmit={handleSubmit} className="border-t border-neutral-200/70 dark:border-neutral-800 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-md px-4 py-4">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isSending}
            className="input-field dark:bg-neutral-800 dark:border-neutral-700 dark:text-white dark:placeholder:text-neutral-500 flex-1"
          />
          <button type="submit" disabled={isSending || !input.trim()} className="btn-primary shrink-0">
            Send
          </button>
        </div>
      </form>
    </div>
  );
}