// src/components/PaymentPriorities.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function PaymentPriorities() {
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    // Fetch all invoices with priority score (placeholder endpoint)
    axios.get("http://localhost:8000/invoice/upload")
      .then(() => {
        // No real data – placeholder empty list
        setInvoices([]);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Payment Priorities</h2>
      {invoices.length === 0 ? (
        <p className="text-gray-400">No invoices yet. Upload an invoice to see priorities.</p>
      ) : (
        <table className="min-w-full bg-surface rounded">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left">Invoice #</th>
              <th className="px-4 py-2 text-left">Vendor</th>
              <th className="px-4 py-2 text-left">Amount</th>
              <th className="px-4 py-2 text-left">Priority</th>
              <th className="px-4 py-2 text-left">Recommendation</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id} className="border-b border-gray-700">
                <td className="px-4 py-2">{inv.invoice_number}</td>
                <td className="px-4 py-2">{inv.vendor_name}</td>
                <td className="px-4 py-2">{inv.currency} {inv.amount}</td>
                <td className="px-4 py-2">{inv.priority_score}</td>
                <td className="px-4 py-2">{inv.recommendation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
