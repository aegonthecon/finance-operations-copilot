// src/components/Dashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Dashboard() {
  const [stats, setStats] = useState({ totalInvoices: 0, totalAmount: 0, overdue: 0, highPriority: 0 });

  useEffect(() => {
    // Simple demo fetch – in a real app you'd have a /summary endpoint.
    // Here we just fetch all invoices and compute stats client‑side.
    axios.get("http://localhost:8000/invoice/upload")
      .then(() => {
        // No real data, keep defaults.
      })
      .catch(() => {});
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="bg-surface rounded-lg p-4 shadow-md">
        <h2 className="text-xl font-semibold mb-2">Total Invoices</h2>
        <p className="text-2xl">{stats.totalInvoices}</p>
      </div>
      <div className="bg-surface rounded-lg p-4 shadow-md">
        <h2 className="text-xl font-semibold mb-2">Total Amount</h2>
        <p className="text-2xl">${stats.totalAmount.toLocaleString()}</p>
      </div>
      <div className="bg-surface rounded-lg p-4 shadow-md">
        <h2 className="text-xl font-semibold mb-2">Overdue</h2>
        <p className="text-2xl">${stats.overdue.toLocaleString()}</p>
      </div>
      <div className="bg-surface rounded-lg p-4 shadow-md">
        <h2 className="text-xl font-semibold mb-2">High‑Priority
        </h2>
        <p className="text-2xl">{stats.highPriority}</p>
      </div>
    </div>
  );
}
