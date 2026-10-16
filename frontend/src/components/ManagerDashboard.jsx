import React, { useState, useEffect } from "react";
import { api } from "../api/client";
import { ShieldAlert, Clock, Users } from "lucide-react";

export default function ManagerDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/analytics/manager-metrics/")
      .then((res) => setMetrics(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-xs text-slate-400">Aggregating real-time queue metrics...</div>;
  }

  if (!metrics) return null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 mb-1">Total System Tickets</div>
          <div className="text-2xl font-bold text-slate-900">{metrics.total_tickets}</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold text-rose-600 mb-1 flex items-center space-x-1">
            <ShieldAlert size={14} />
            <span>SLA Breaches</span>
          </div>
          <div className="text-2xl font-bold text-rose-600">{metrics.sla_breached_count}</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 mb-1 flex items-center space-x-1">
            <Clock size={14} />
            <span>Avg Response (mins)</span>
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {metrics.avg_first_response_minutes ?? "N/A"}
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 mb-1 flex items-center space-x-1">
            <Users size={14} />
            <span>Active Staff</span>
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.agent_workload.length}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-4">Tickets by Priority</h3>
          <div className="space-y-2">
            {Object.entries(metrics.tickets_by_priority).map(([priority, count]) => (
              <div key={priority} className="flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-700">{priority}</span>
                <span className="bg-slate-100 px-2 py-0.5 rounded font-bold text-slate-800">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-4">Agent Workload Distribution</h3>
          <div className="space-y-3">
            {metrics.agent_workload.map((agent) => (
              <div key={agent.id} className="text-xs">
                <div className="flex justify-between font-semibold text-slate-700 mb-1">
                  <span>{agent.email}</span>
                  <span>{agent.active_tickets} active tickets</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div
                    className="bg-indigo-600 h-1.5 rounded-full"
                    style={{ width: `${Math.min(agent.active_tickets * 15, 100)}%` }}
                  />
                </div>
              </div>
            ))}
            {metrics.agent_workload.length === 0 && (
              <div className="text-xs text-slate-400">No active support personnel assigned.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}