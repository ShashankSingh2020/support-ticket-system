import React, { useState, useEffect } from "react";
import { api } from "./api/client";
import Navbar from "./components/Navbar";
import LoginModal from "./components/LoginModal";
import TicketList from "./components/TicketList";
import TicketDetail from "./components/TicketDetail";
import CreateTicketModal from "./components/CreateTicketModal";
import ManagerDashboard from "./components/ManagerDashboard";

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem("currentUser");
    return saved ? JSON.parse(saved) : null;
  });
  const [tickets, setTickets] = useState([]);
  const [selectedTicketId, setSelectedTicketId] = useState(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("tickets");

  const fetchTickets = async () => {
    if (!currentUser) return;
    try {
      const res = await api.get("/tickets/");
      setTickets(res.data);
      if (!selectedTicketId && res.data.length > 0) {
        setSelectedTicketId(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [currentUser]);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("currentUser");
    setCurrentUser(null);
    setTickets([]);
    setSelectedTicketId(null);
  };

  if (!currentUser) {
    return <LoginModal onLoginSuccess={(user) => setCurrentUser(user)} />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar
        user={currentUser}
        onLogout={handleLogout}
        onOpenCreate={() => setIsCreateOpen(true)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main className="max-w-7xl w-full mx-auto p-6 flex-1">
        {activeTab === "analytics" && (currentUser.role === "MANAGER" || currentUser.role === "ADMIN") ? (
          <ManagerDashboard />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  {currentUser.role === "CUSTOMER" ? "My Tickets" : "Assigned Support Queue"}
                </h3>
                <span className="text-xs bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full font-bold">
                  {tickets.length}
                </span>
              </div>
              <TicketList
                tickets={tickets}
                onSelectTicket={(id) => setSelectedTicketId(id)}
                selectedId={selectedTicketId}
              />
            </div>

            <div className="lg:col-span-7">
              {selectedTicketId ? (
                <TicketDetail
                  ticketId={selectedTicketId}
                  currentUser={currentUser}
                  onTicketUpdated={fetchTickets}
                />
              ) : (
                <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-xs text-slate-400">
                  Select a ticket from the left queue to view details.
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <CreateTicketModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreated={fetchTickets}
      />
    </div>
  );
}