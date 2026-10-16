import React from "react";
import { AlertCircle, Clock, CheckCircle2, Bot, Layers, Network } from "lucide-react";

export default function TicketList({ tickets, onSelectTicket, selectedId }) {
  const getPriorityBadge = (priority) => {
    switch (priority) {
      case "CRITICAL":
        return "bg-rose-100 text-rose-800 border-rose-200";
      case "HIGH":
        return "bg-amber-100 text-amber-800 border-amber-200";
      case "MEDIUM":
        return "bg-sky-100 text-sky-800 border-sky-200";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "OPEN":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "IN_PROGRESS":
        return "bg-purple-50 text-purple-700 border-purple-200";
      case "WAITING_CUSTOMER":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "RESOLVED":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "CLOSED":
        return "bg-slate-100 text-slate-600 border-slate-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  if (!tickets.length) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
        <CheckCircle2 className="text-slate-300 mx-auto mb-2" size={36} />
        <h4 className="text-sm font-semibold text-slate-700">No Tickets Found</h4>
        <p className="text-xs text-slate-400">Queue is currently clear.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="divide-y divide-slate-100">
        {tickets.map((t) => {
          const isSelected = selectedId === t.id;
          return (
            <div
              key={t.id}
              onClick={() => onSelectTicket(t.id)}
              className={`p-4 cursor-pointer transition flex items-center justify-between hover:bg-slate-50/80 ${
                isSelected ? "bg-indigo-50/40 border-l-4 border-indigo-600" : ""
              }`}
            >
              <div className="space-y-1.5 max-w-[72%]">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getPriorityBadge(
                      t.priority
                    )}`}
                  >
                    {t.priority}
                  </span>
                  <span
                    className={`text-[10px] font-medium px-2 py-0.5 rounded border ${getStatusBadge(
                      t.status
                    )}`}
                  >
                    {t.status.replace("_", " ")}
                  </span>

                  {t.is_master_incident && (
                    <span className="flex items-center space-x-1 text-[10px] font-bold text-violet-800 bg-violet-100 px-1.5 py-0.5 rounded border border-violet-200">
                      <Layers size={10} />
                      <span>MASTER INCIDENT</span>
                    </span>
                  )}

                  {t.parent_incident && (
                    <span className="flex items-center space-x-1 text-[10px] font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-200">
                      <Network size={10} />
                      <span>LINKED TO OUTAGE</span>
                    </span>
                  )}

                  {t.sla_breached && (
                    <span className="flex items-center space-x-1 text-[10px] font-semibold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">
                      <AlertCircle size={10} />
                      <span>SLA BREACHED</span>
                    </span>
                  )}
                </div>

                <h4 className="text-sm font-semibold text-slate-900 truncate">{t.title}</h4>

                <div className="flex items-center space-x-3 text-[11px] text-slate-500">
                  <span className="truncate max-w-[140px]">{t.customer_email}</span>
                  <span>•</span>
                  <span>{t.category}</span>
                  {t.ai_status === "COMPLETED" && (
                    <>
                      <span>•</span>
                      <span className="flex items-center space-x-1 text-indigo-600 font-medium">
                        <Bot size={12} />
                        <span>AI Triaged</span>
                      </span>
                    </>
                  )}
                </div>
              </div>

              <div className="text-right text-[11px] text-slate-400 flex items-center space-x-1 shrink-0">
                <Clock size={12} />
                <span>
                  {new Date(t.created_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}