"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { API_BASE_URL } from "@/lib/constants";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatPage() {
  const { botId } = useParams<{ botId: string }>();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/${botId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage.content }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Chat failed");
        return;
      }

      const botMessage: Message = {
        role: "assistant",
        content: data.answer,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b p-4">
        <h1 className="text-lg font-semibold">
          Chatbot
        </h1>
        <p className="text-xs text-gray-500">
          Bot ID: {botId}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 space-y-3 overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-sm text-gray-500">
            Ask anything about the website.
          </p>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-xl px-4 py-2 rounded ${
              msg.role === "user"
                ? "bg-black text-white ml-auto"
                : "bg-white border"
            }`}
          >
            {msg.content}
          </div>
        ))}

        {loading && (
          <p className="text-sm text-gray-500">
            Thinking…
          </p>
        )}

        {error && (
          <p className="text-sm text-red-600">
            {error}
          </p>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={sendMessage}
        className="bg-white border-t p-4 flex gap-2"
      >
        <input
          type="text"
          placeholder="Ask a question..."
          className="flex-1 border p-2 rounded"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading}
          className="bg-black text-white px-4 rounded"
        >
          Send
        </button>
      </form>
    </div>
  );
}