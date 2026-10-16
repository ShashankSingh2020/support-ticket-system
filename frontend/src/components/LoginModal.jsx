import React, { useState } from "react";
import { api } from "../api/client";
import { KeyRound, ShieldAlert } from "lucide-react";

export default function LoginModal({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e, customEmail = null, customPass = null) => {
    if (e) e.preventDefault();
    setError("");
    setLoading(true);

    const targetEmail = customEmail || email;
    const targetPass = customPass || password;

    try {
      const res = await api.post("/users/auth/login/", {
        email: targetEmail,
        password: targetPass,
      });

      localStorage.setItem("accessToken", res.data.access);
      localStorage.setItem("currentUser", JSON.stringify(res.data.user));
      onLoginSuccess(res.data.user);
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed. Verify credentials.");
    } finally {
      setLoading(false);
    }
  };

  const fillAndSubmit = (demoEmail) => {
    setEmail(demoEmail);
    setPassword("TestPass123!");
    handleLogin(null, demoEmail, "TestPass123!");
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
        <div className="text-center mb-6">
          <div className="inline-flex p-3 bg-indigo-50 rounded-xl text-indigo-600 mb-3">
            <KeyRound size={28} />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Sign in to SupportOps</h2>
          <p className="text-sm text-slate-500 mt-1">Authenticate using your credentials or demo roles</p>
        </div>

        {error && (
          <div className="mb-4 flex items-center space-x-2 text-rose-700 bg-rose-50 border border-rose-200 text-xs p-3 rounded-lg">
            <ShieldAlert size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="user@system.local"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition"
          >
            {loading ? "Authenticating..." : "Sign In"}
          </button>
        </form>

        <div className="mt-8 border-t border-slate-100 pt-6">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 text-center mb-3">
            Quick-Login Seed Personas
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => fillAndSubmit("customer@client.local")}
              className="text-left px-3 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs transition"
            >
              <div className="font-semibold text-slate-800">Customer</div>
              <div className="text-[10px] text-slate-500">customer@client.local</div>
            </button>
            <button
              type="button"
              onClick={() => fillAndSubmit("agent@system.local")}
              className="text-left px-3 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs transition"
            >
              <div className="font-semibold text-slate-800">Agent</div>
              <div className="text-[10px] text-slate-500">agent@system.local</div>
            </button>
            <button
              type="button"
              onClick={() => fillAndSubmit("manager@system.local")}
              className="text-left px-3 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs transition"
            >
              <div className="font-semibold text-slate-800">Manager</div>
              <div className="text-[10px] text-slate-500">manager@system.local</div>
            </button>
            <button
              type="button"
              onClick={() => fillAndSubmit("admin@system.local")}
              className="text-left px-3 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs transition"
            >
              <div className="font-semibold text-slate-800">Admin</div>
              <div className="text-[10px] text-slate-500">admin@system.local</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}