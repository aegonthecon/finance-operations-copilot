import React, { useEffect, useState } from "react";
import axios from "axios";

export default function VendorAnalytics() {
  const [vendors, setVendors] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/dashboard/vendors")
      .then(res => setVendors(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-teal-400">Vendor Intelligence</h1>

      {vendors.length === 0 ? (
        <div className="bg-surface p-8 text-center rounded shadow-md border border-gray-700">
          <p className="text-gray-400">No vendor data available. Upload invoices to build intelligence.</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-surface rounded-lg shadow-md border border-gray-700">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Vendor</th>
                <th className="px-4 py-3 text-left font-semibold">Category</th>
                <th className="px-4 py-3 text-left font-semibold">Invoices</th>
                <th className="px-4 py-3 text-left font-semibold">Total Spend</th>
                <th className="px-4 py-3 text-left font-semibold">Risk / AI Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {vendors.sort((a,b) => b.total_spend - a.total_spend).map((v, i) => (
                <tr key={i} className="hover:bg-gray-800 transition-colors">
                  <td className="px-4 py-3 font-medium">{v.vendor_name}</td>
                  <td className="px-4 py-3">
                    <span className="bg-gray-700 text-gray-200 px-2 py-1 rounded text-xs">
                      {v.category}
                    </span>
                  </td>
                  <td className="px-4 py-3">{v.invoice_count}</td>
                  <td className="px-4 py-3 font-bold">${v.total_spend.toLocaleString()}</td>
                  <td className="px-4 py-3 text-gray-400 max-w-xs truncate" title={v.risk_notes}>
                    {v.risk_notes || "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
