import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import {
  Bot,
  Lock,
  Send,
  RefreshCw,
  AlertTriangle,
  Layers,
  Network,
  CheckCircle,
} from "lucide-react";

export default function TicketDetail({ ticketId, currentUser, onTicketUpdated }) {
  const [ticket, setTicket] = useState(null);
  const [replies, setReplies] = useState([]);
  const [content, setContent] = useState("");
  const [isInternal, setIsInternal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchDetails = async () => {
    try {
      const [tRes, rRes] = await Promise.all([
        api.get(`/tickets/${ticketId}/`),
        api.get(`/tickets/${ticketId}/replies/`),
      ]);
      setTicket(tRes.data);
      setReplies(rRes.data);
    } catch (err) {
      console.error("Failed to fetch ticket thread:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ticketId) {
      setLoading(true);
      fetchDetails();
    }
  }, [ticketId]);

  const handleSendReply = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;
    setSubmitting(true);
    try {
      await api.post(`/tickets/${ticketId}/replies/`, {
        content,
        is_internal: isInternal,
      });
      setContent("");
      setIsInternal(false);
      fetchDetails();
      onTicketUpdated();
    } catch {
      alert("Failed to submit reply.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await api.post(`/tickets/${ticketId}/transition-status/`, { status: newStatus });
      fetchDetails();
      onTicketUpdated();
    } catch (err) {
      alert(err.response?.data?.error || "Status transition prohibited.");
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading ticket thread...</div>;
  }

  if (!ticket) return null;

  const isStaff = ["AGENT", "MANAGER", "ADMIN"].includes(currentUser.role);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[750px]">
      {/* Header */}
      <div className="p-5 border-b border-slate-100 flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-bold text-slate-500">#{ticket.id.slice(0, 8)}</span>
            <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">
              {ticket.category}
            </span>
            <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-semibold uppercase">
              {ticket.priority}
            </span>

            {ticket.is_master_incident && (
              <span className="flex items-center space-x-1 text-xs font-bold text-violet-800 bg-violet-100 px-2 py-0.5 rounded border border-violet-200">
                <Layers size={12} />
                <span>MASTER INCIDENT CLUSTER</span>
              </span>
            )}

            {ticket.parent_incident && (
              <span className="flex items-center space-x-1 text-xs font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                <Network size={12} />
                <span>LINKED TO INCIDENT #{ticket.parent_incident.slice(0, 8)}</span>
              </span>
            )}
          </div>
          <h2 className="text-base font-bold text-slate-900">{ticket.title}</h2>
          <p className="text-xs text-slate-500">Reported by {ticket.customer_email}</p>
        </div>

        {isStaff && (
          <div className="flex items-center space-x-2 shrink-0">
            <select
              value={ticket.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="OPEN">Open</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="WAITING_CUSTOMER">Waiting for Customer</option>
              <option value="RESOLVED">Resolved</option>
              <option value="CLOSED">Closed</option>
            </select>
            <button
              onClick={fetchDetails}
              className="p-1.5 text-slate-400 hover:text-slate-600 rounded"
              title="Refresh Thread"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Outage Banner for Linked Tickets */}
      {ticket.parent_incident && (
        <div className="bg-amber-50 border-b border-amber-200 px-5 py-2.5 flex items-center justify-between text-xs text-amber-900">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="text-amber-600 shrink-0" size={15} />
            <span>
              This ticket is grouped under active Outage Surge Incident{" "}
              <strong className="font-semibold">#{ticket.parent_incident.slice(0, 8)}</strong>.
            </span>
          </div>
          <span className="text-[11px] font-semibold text-amber-700 bg-amber-100 px-2 py-0.5 rounded border border-amber-300">
            Auto-Broadcast Active
          </span>
        </div>
      )}

      {/* Master Incident Banner for Staff */}
      {ticket.is_master_incident && isStaff && (
        <div className="bg-violet-50 border-b border-violet-200 px-5 py-2.5 flex items-center justify-between text-xs text-violet-950">
          <div className="flex items-center space-x-2">
            <Layers className="text-violet-600 shrink-0" size={15} />
            <span>
              This is the <strong className="font-semibold">Master Incident</strong>. Resolving
              this ticket will automatically cascade resolution updates to all linked child tickets.
            </span>
          </div>
          <span className="text-[11px] font-bold text-violet-700 bg-violet-100 px-2 py-0.5 rounded border border-violet-300">
            Outage Lead
          </span>
        </div>
      )}

      {/* AI Context Card */}
      {ticket.ai_summary && (
        <div className="bg-gradient-to-r from-indigo-50/60 to-purple-50/60 border-b border-indigo-100 p-3 px-5 flex items-start space-x-2.5">
          <Bot className="text-indigo-600 mt-0.5 shrink-0" size={16} />
          <div className="text-xs">
            <span className="font-semibold text-indigo-950">AI Triaged Synopsis: </span>
            <span className="text-indigo-900">{ticket.ai_summary}</span>
          </div>
        </div>
      )}

      {/* Reply Thread */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {/* Original Issue */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4">
          <div className="text-[11px] font-semibold text-slate-500 mb-1">
            Original Issue Description
          </div>
          <p className="text-sm text-slate-800 whitespace-pre-wrap">{ticket.description}</p>
        </div>

        {replies.map((r) => {
          const isAutomatedBroadcast =
            r.content.includes("Automated Notification:") ||
            r.content.includes("Resolution Update:");

          return (
            <div
              key={r.id}
              className={`p-4 rounded-xl border ${
                r.is_internal
                  ? "bg-amber-50/70 border-amber-200"
                  : isAutomatedBroadcast
                  ? "bg-indigo-50/40 border-indigo-200"
                  : "bg-white border-slate-200 shadow-sm"
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-slate-900">{r.author_email}</span>
                  <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                    {r.author_role}
                  </span>

                  {isAutomatedBroadcast && (
                    <span className="flex items-center space-x-1 text-[10px] font-bold text-indigo-800 bg-indigo-100 px-1.5 py-0.5 rounded border border-indigo-200">
                      <Network size={10} />
                      <span>SURGE BROADCAST</span>
                    </span>
                  )}

                  {r.is_internal && (
                    <span className="flex items-center space-x-1 text-[10px] font-bold text-amber-800 bg-amber-100 px-1.5 py-0.5 rounded border border-amber-300">
                      <Lock size={10} />
                      <span>INTERNAL NOTE</span>
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-slate-400">
                  {new Date(r.created_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
              <p className="text-sm text-slate-700 whitespace-pre-wrap">{r.content}</p>
            </div>
          );
        })}
      </div>

      {/* Composer */}
      {ticket.status !== "CLOSED" ? (
        <form onSubmit={handleSendReply} className="p-4 border-t border-slate-100 bg-slate-50/50">
          {isStaff && (
            <div className="flex items-center space-x-2 mb-2">
              <label className="flex items-center space-x-1.5 text-xs text-slate-700 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={isInternal}
                  onChange={(e) => setIsInternal(e.target.checked)}
                  className="rounded text-amber-600 focus:ring-amber-500"
                />
                <span className="font-semibold text-amber-900">Post as Agent Internal Note</span>
              </label>
            </div>
          )}

          <div className="flex space-x-2">
            <textarea
              rows={2}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={
                isInternal
                  ? "Write internal staff observation..."
                  : "Reply to customer (or post cluster update)..."
              }
              className={`flex-1 p-2.5 text-sm border rounded-lg focus:outline-none focus:ring-2 ${
                isInternal
                  ? "border-amber-300 focus:ring-amber-500 bg-amber-50/30"
                  : "border-slate-200 focus:ring-indigo-500 bg-white"
              }`}
            />
            <button
              type="submit"
              disabled={submitting}
              className={`px-4 flex items-center justify-center rounded-lg text-white transition ${
                isInternal
                  ? "bg-amber-600 hover:bg-amber-700"
                  : "bg-indigo-600 hover:bg-indigo-700"
              }`}
            >
              <Send size={16} />
            </button>
          </div>
        </form>
      ) : (
        <div className="p-4 text-center text-xs font-semibold text-slate-400 bg-slate-50 border-t border-slate-100 flex items-center justify-center space-x-1.5">
          <CheckCircle size={14} className="text-slate-400" />
          <span>This ticket is closed and archived.</span>
        </div>
      )}
    </div>
  );
}