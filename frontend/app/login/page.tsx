"use client";

import { useState } from "react";
import { saveToken, getToken } from "@/lib/auth";
import { API_BASE_URL } from "@/lib/constants";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // 👇 bot creation states
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [creating, setCreating] = useState(false);
  const [botId, setBotId] = useState<string | null>(null);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Login failed");
        return;
      }

      saveToken(data.access_token);
    } catch {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateBot(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE_URL}/bots/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ website_url: websiteUrl }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Failed to create bot");
        return;
      }

      setBotId(data.bot_id);
    } catch {
      setError("Failed to create bot");
    } finally {
      setCreating(false);
    }
  }

  const isLoggedIn = Boolean(getToken());

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-6 rounded shadow w-96">
        {!isLoggedIn ? (
          <>
            <h1 className="text-xl font-bold mb-4">Login</h1>

            {error && (
              <p className="text-red-600 text-sm mb-2">{error}</p>
            )}

            <form onSubmit={handleLogin}>
              <input
                type="email"
                placeholder="Email"
                className="w-full border p-2 mb-3"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <input
                type="password"
                placeholder="Password"
                className="w-full border p-2 mb-4"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-black text-white py-2"
              >
                {loading ? "Logging in..." : "Login"}
              </button>
            </form>
          </>
        ) : (
          <>
            <h1 className="text-xl font-bold mb-4">Create Bot</h1>

            {error && (
              <p className="text-red-600 text-sm mb-2">{error}</p>
            )}

            <form onSubmit={handleCreateBot}>
              <input
                type="url"
                placeholder="Website URL"
                className="w-full border p-2 mb-4"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                required
              />

              <button
                type="submit"
                disabled={creating}
                className="w-full bg-black text-white py-2"
              >
                {creating ? "Creating..." : "Create Bot"}
              </button>
            </form>

            {botId && (
              <p className="text-green-600 text-sm mt-4">
                ✅ Bot created successfully  
                <br />
                Bot ID: <strong>{botId}</strong>
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
