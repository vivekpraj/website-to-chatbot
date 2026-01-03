"use client";

import { useEffect, useState } from "react";
import { getToken, getUserRole } from "@/lib/auth";
import { API_BASE_URL } from "@/lib/constants";

type Bot = {
  bot_id: string;
  website_url: string;
  status: string;
  message_count: number;
  owner_email: string;
  created_at: string;
};

export default function AdminBotsPage() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const role = getUserRole();
    if (role !== "super_admin") {
      window.location.href = "/dashboard";
      return;
    }

    fetchBots();
  }, []);

  async function fetchBots() {
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/admin/bots`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      if (res.ok) {
        setBots(data);
      }
    } finally {
      setLoading(false);
    }
  }

  async function deleteBot(botId: string) {
    if (!confirm("Delete this bot?")) return;

    try {
      const token = getToken();
      await fetch(`${API_BASE_URL}/admin/bots/${botId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setBots((prev) => prev.filter((b) => b.bot_id !== botId));
    } catch {
      alert("Failed to delete bot");
    }
  }

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-6">Admin – Bots</h1>

      {loading && <p>Loading bots...</p>}

      <div className="space-y-4">
        {bots.map((bot) => (
          <div
            key={bot.bot_id}
            className="border p-4 rounded bg-gray-50"
          >
            <p><strong>Website:</strong> {bot.website_url}</p>
            <p><strong>Owner:</strong> {bot.owner_email}</p>
            <p><strong>Status:</strong> {bot.status}</p>
            <p><strong>Messages:</strong> {bot.message_count}</p>

            <button
              onClick={() => deleteBot(bot.bot_id)}
              className="text-red-600 mt-2"
            >
              Delete Bot
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}