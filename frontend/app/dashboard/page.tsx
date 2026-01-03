"use client";

import { useState, useEffect } from "react";
import {
  getToken,
  getUserRole,
  logout,
} from "@/lib/auth";
import { API_BASE_URL } from "@/lib/constants";
import Link from "next/link";

type Bot = {
  bot_id: string;
  website_url: string;
  status: string;
  created_at: string;
};

export default function DashboardPage() {
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [bots, setBots] = useState<Bot[]>([]);
  const [loadingBots, setLoadingBots] = useState(true);

  const [role, setRole] = useState<string | null>(null);

  // ---------------------------------------
  // AUTH + ROLE CHECK
  // ---------------------------------------
  useEffect(() => {
    const token = getToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    setRole(getUserRole());

    async function fetchBots() {
      try {
        const res = await fetch(`${API_BASE_URL}/bots/my`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await res.json();
        if (res.ok) {
          setBots(data);
        }
      } catch {
        console.error("Failed to fetch bots");
      } finally {
        setLoadingBots(false);
      }
    }

    fetchBots();
  }, []);

  // ---------------------------------------
  // CREATE BOT (CLIENT)
  // ---------------------------------------
  async function handleCreateBot(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const token = getToken();

      const res = await fetch(`${API_BASE_URL}/bots/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ website_url: websiteUrl }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Failed to create bot");
        return;
      }

      setMessage("Bot created successfully!");
      setWebsiteUrl("");

      setBots((prev) => [data, ...prev]);
    } catch {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-10">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow">

        {/* HEADER */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <button
            onClick={logout}
            className="text-sm text-red-600 underline"
          >
            Logout
          </button>
        </div>

        {/* ROLE INFO */}
        <p className="text-sm text-gray-500 mb-6">
          Logged in as: <strong>{role}</strong>
        </p>

        {/* ================= CLIENT UI ================= */}
        {role === "client" && (
          <>
            <h2 className="text-lg font-semibold mb-3">
              Create New Bot
            </h2>

            <form onSubmit={handleCreateBot}>
              <input
                type="url"
                placeholder="Enter website URL"
                className="w-full border p-2 mb-3"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                required
              />

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-black text-white py-2"
              >
                {loading ? "Creating bot..." : "Create Bot"}
              </button>
            </form>

            {message && (
              <p className="text-green-600 text-sm mt-3">
                {message}
              </p>
            )}

            {error && (
              <p className="text-red-600 text-sm mt-3">
                {error}
              </p>
            )}
          </>
        )}

        {/* ================= BOT LIST ================= */}
        <hr className="my-6" />

        <h2 className="text-lg font-semibold mb-3">
          Your Bots
        </h2>

        {loadingBots && (
          <p className="text-sm text-gray-500">
            Loading bots...
          </p>
        )}

        {!loadingBots && bots.length === 0 && (
          <p className="text-sm text-gray-500">
            No bots created yet.
          </p>
        )}

        <div className="space-y-3">
          {bots.map((bot) => {
            const chatUrl = `${window.location.origin}/chat/${bot.bot_id}`;

            return (
              <div
                key={bot.bot_id}
                className="border p-3 rounded bg-gray-50"
              >
                <p className="text-sm">
                  <strong>Website:</strong> {bot.website_url}
                </p>

                <p className="text-sm">
                  <strong>Status:</strong>{" "}
                  <span
                    className={
                      bot.status === "ready"
                        ? "text-green-600"
                        : bot.status === "processing"
                        ? "text-yellow-600"
                        : "text-red-600"
                    }
                  >
                    {bot.status}
                  </span>
                </p>

                <p className="text-xs break-all">
                  <strong>Chat URL:</strong>{" "}
                  <a
                    href={chatUrl}
                    target="_blank"
                    className="text-blue-600 underline"
                  >
                    {chatUrl}
                  </a>
                </p>
              </div>
            );
          })}
        </div>

        {/* ================= SUPER ADMIN UI ================= */}
        {role === "super_admin" && (
          <>
            <hr className="my-6" />
            <h2 className="text-lg font-semibold mb-3">
              Admin Controls
            </h2>

            <div className="space-y-2">
  <Link
    href="/admin/users"
    className="block w-full text-center border py-2 hover:bg-gray-50"
  >
    View All Users
  </Link>

  <Link
    href="/admin/bots"
    className="block w-full text-center border py-2 hover:bg-gray-50"
  >
    View All Bots
  </Link>
</div>
          </>
        )}
      </div>
    </div>
  );
}
