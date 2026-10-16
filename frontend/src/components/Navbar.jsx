import React from "react";
import { ShieldCheck, LogOut, PlusCircle, BarChart3, Inbox } from "lucide-react";

export default function Navbar({ user, onLogout, onOpenCreate, activeTab, setActiveTab }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-20">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-indigo-600 text-white p-2 rounded-lg">
            <ShieldCheck size={20} />
          </div>
          <div>
            <span className="font-bold text-slate-900 tracking-tight text-lg">SupportOps</span>
            <span className="ml-2 text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full border border-slate-200">
              AI Triage
            </span>
          </div>
        </div>

        {user ? (
          <div className="flex items-center space-x-4">
            <nav className="flex items-center space-x-1 mr-2">
              <button
                onClick={() => setActiveTab("tickets")}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition ${
                  activeTab === "tickets"
                    ? "bg-slate-100 text-slate-900"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Inbox size={16} />
                <span>Queue</span>
              </button>

              {(user.role === "MANAGER" || user.role === "ADMIN") && (
                <button
                  onClick={() => setActiveTab("analytics")}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition ${
                    activeTab === "analytics"
                      ? "bg-slate-100 text-slate-900"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <BarChart3 size={16} />
                  <span>Metrics</span>
                </button>
              )}
            </nav>

            {user.role === "CUSTOMER" && (
              <button
                onClick={onOpenCreate}
                className="flex items-center space-x-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-3.5 py-1.5 rounded-lg shadow-sm transition"
              >
                <PlusCircle size={16} />
                <span>New Ticket</span>
              </button>
            )}

            <div className="border-l border-slate-200 pl-4 flex items-center space-x-3">
              <div className="text-right">
                <p className="text-xs font-semibold text-slate-900">{user.email}</p>
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
                  {user.role}
                </span>
              </div>
              <button
                onClick={onLogout}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-md transition"
                title="Log out"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </header>
  );
}