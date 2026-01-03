"use client";

import { useEffect, useState } from "react";
import { getToken, getUserRole } from "@/lib/auth";
import { API_BASE_URL } from "@/lib/constants";

type User = {
  id: number;
  email: string;
  role: string;
  created_at: string;
};

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const role = getUserRole();
    if (role !== "super_admin") {
      window.location.href = "/dashboard";
      return;
    }

    fetchUsers();
  }, []);

  async function fetchUsers() {
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/admin/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Failed to load users");
        return;
      }

      setUsers(data);
    } catch {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function deleteUser(userId: number) {
    if (!confirm("Are you sure you want to delete this user?")) return;

    try {
      const token = getToken();
      await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch {
      alert("Failed to delete user");
    }
  }

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-6">Admin – Users</h1>

      {loading && <p>Loading users...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {!loading && users.length === 0 && <p>No users found.</p>}

      <table className="w-full border">
        <thead className="bg-gray-100">
          <tr>
            <th className="border p-2">ID</th>
            <th className="border p-2">Email</th>
            <th className="border p-2">Role</th>
            <th className="border p-2">Created</th>
            <th className="border p-2">Action</th>
          </tr>
        </thead>

        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td className="border p-2">{user.id}</td>
              <td className="border p-2">{user.email}</td>
              <td className="border p-2">{user.role}</td>
              <td className="border p-2">
                {new Date(user.created_at).toLocaleString()}
              </td>
              <td className="border p-2">
                {user.role !== "super_admin" && (
                  <button
                    onClick={() => deleteUser(user.id)}
                    className="text-red-600"
                  >
                    Delete
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
