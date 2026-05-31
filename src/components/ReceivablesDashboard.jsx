// src/components/ReceivablesDashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function ReceivablesDashboard() {
  const [receivables, setReceivables] = useState([]);

  useEffect(() => {
    // Placeholder fetch – in a real app you'd call a /receivable/list endpoint
    axios.get("http://localhost:8000/receivable/upload")
      .then(() => {
        // No real data yet; keep empty list
        setReceivables([]);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Accounts Receivable</h2>
      {receivables.length === 0 ? (
        <p className="text-gray-400">No receivable data. Upload receivables to view priorities.</p>
      ) : (
        <table className="min-w-full bg-surface rounded">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left">Customer</th>
              <th className="px-4 py-2 text-left">Amount Due</th>
              <th className="px-4 py-2 text-left">Days Overdue</th>
              <th className="px-4 py-2 text-left">Priority Score</th>
            </tr>
          </thead>
          <tbody>
            {receivables.map((r) => (
              <tr key={r.id} className="border-b border-gray-700">
                <td className="px-4 py-2">{r.customer}</td>
                <td className="px-4 py-2">{r.amount_due}</td>
                <td className="px-4 py-2">{r.days_overdue}</td>
                <td className="px-4 py-2">{r.priority_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
