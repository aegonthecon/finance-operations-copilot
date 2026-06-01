import React, { useEffect, useState } from "react";
import axios from "axios";

export default function ReceivablesDashboard() {
  const [receivables, setReceivables] = useState([]);
  const [loading, setLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(null);

  const fetchReceivables = () => {
    axios.get("http://localhost:8000/receivable")
      .then(res => setReceivables(res.data))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchReceivables();
  }, []);

  const handleMockSync = async () => {
    setLoading(true);
    try {
      await axios.post("http://localhost:8000/receivable/mock_sync");
      fetchReceivables();
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleGenerateEmail = async (id, reminderType) => {
    setEmailLoading(id);
    try {
      await axios.get(`http://localhost:8000/receivable/${id}/email?reminder_type=${reminderType}`);
      fetchReceivables();
    } catch (err) {
      console.error(err);
    }
    setEmailLoading(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-teal-400">Accounts Receivable Workflow</h1>
        <button 
          onClick={handleMockSync}
          disabled={loading}
          className="bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 px-4 rounded shadow disabled:opacity-50"
        >
          {loading ? "Syncing..." : "Sync ERP Data (Mock)"}
        </button>
      </div>

      {receivables.length === 0 ? (
        <div className="bg-surface p-8 text-center rounded shadow-md border border-gray-700">
          <p className="text-gray-400">No AR data found. Click Sync to fetch mock records.</p>
        </div>
      ) : (
        <div className="overflow-x-auto bg-surface rounded-lg shadow-md border border-gray-700">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Customer</th>
                <th className="px-4 py-3 text-left font-semibold">Amount Due</th>
                <th className="px-4 py-3 text-left font-semibold">Days Overdue</th>
                <th className="px-4 py-3 text-left font-semibold">Risk</th>
                <th className="px-4 py-3 text-left font-semibold">Recommendation</th>
                <th className="px-4 py-3 text-left font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {receivables.sort((a,b) => b.priority_score - a.priority_score).map((r) => (
                <tr key={r.id} className="hover:bg-gray-800 transition-colors">
                  <td className="px-4 py-3 font-medium">{r.customer}</td>
                  <td className="px-4 py-3">${r.amount_due?.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <span className={r.days_overdue > 30 ? "text-red-400 font-bold" : (r.days_overdue > 0 ? "text-orange-400" : "text-green-400")}>
                      {r.days_overdue}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      r.customer_risk === 'High' ? 'bg-red-900 text-red-200' :
                      r.customer_risk === 'Medium' ? 'bg-orange-900 text-orange-200' :
                      'bg-green-900 text-green-200'
                    }`}>
                      {r.customer_risk || "Unknown"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-300">{r.follow_up_recommendation}</td>
                  <td className="px-4 py-3">
                    {r.email_draft ? (
                      <button className="text-teal-400 underline" onClick={() => alert(r.email_draft)}>View Draft</button>
                    ) : (
                      <div className="flex space-x-2 items-center">
                        <select id={`type-${r.id}`} className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs outline-none focus:border-teal-500">
                          <option value="Friendly">Friendly</option>
                          <option value="Second">Second</option>
                          <option value="Final">Final</option>
                        </select>
                        <button 
                          onClick={() => handleGenerateEmail(r.id, document.getElementById(`type-${r.id}`).value)}
                          disabled={emailLoading === r.id}
                          className="bg-purple-600 hover:bg-purple-500 text-white text-xs py-1 px-3 rounded shadow disabled:opacity-50"
                        >
                          {emailLoading === r.id ? "Drafting..." : "Draft Email"}
                        </button>
                      </div>
                    )}
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
