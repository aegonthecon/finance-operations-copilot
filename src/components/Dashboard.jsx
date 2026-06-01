import React, { useEffect, useState } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    total_invoices: 0,
    total_payable: 0,
    overdue_amount: 0,
    high_priority_count: 0,
    duplicate_count: 0,
    due_this_week_amount: 0,
    due_this_month_amount: 0,
    overdue_count: 0
  });
  
  const [cashflow, setCashflow] = useState([]);
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    // Fetch metrics
    axios.get("http://localhost:8000/dashboard/metrics")
      .then(res => setMetrics(res.data))
      .catch(err => console.error(err));
      
    // Fetch cashflow
    axios.get("http://localhost:8000/dashboard/cashflow")
      .then(res => setCashflow(res.data))
      .catch(err => console.error(err));

    // Fetch invoices for tracking
    axios.get("http://localhost:8000/invoice")
      .then(res => setInvoices(res.data))
      .catch(err => console.error(err));
  }, []);

  const getStatusBadge = (invoice) => {
    const today = new Date();
    today.setHours(0,0,0,0);
    const dueDate = new Date(invoice.due_date);
    if (dueDate < today) {
      return <span className="bg-red-900 text-red-200 text-xs px-2 py-1 rounded">Overdue</span>;
    } else if ((dueDate - today) <= 7 * 24 * 60 * 60 * 1000) {
      return <span className="bg-orange-900 text-orange-200 text-xs px-2 py-1 rounded">Due Soon</span>;
    }
    return <span className="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded">Upcoming</span>;
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold mb-4 text-teal-400">Finance Dashboard</h1>
      
      {/* Metrics Row 1 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface rounded-lg p-4 shadow-md border-t-4 border-teal-500">
          <h2 className="text-sm font-semibold text-gray-400 mb-1">Total Payable</h2>
          <p className="text-3xl">${metrics.total_payable.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-2">{metrics.total_invoices} Active Invoices</p>
        </div>
        <div className="bg-surface rounded-lg p-4 shadow-md border-t-4 border-red-500">
          <h2 className="text-sm font-semibold text-gray-400 mb-1">Overdue Amount</h2>
          <p className="text-3xl text-red-400">${metrics.overdue_amount.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-2">{metrics.overdue_count} Invoices Overdue</p>
        </div>
        <div className="bg-surface rounded-lg p-4 shadow-md border-t-4 border-orange-500">
          <h2 className="text-sm font-semibold text-gray-400 mb-1">Due Next 7 Days</h2>
          <p className="text-3xl text-orange-400">${metrics.due_this_week_amount.toLocaleString()}</p>
        </div>
        <div className="bg-surface rounded-lg p-4 shadow-md border-t-4 border-purple-500">
          <h2 className="text-sm font-semibold text-gray-400 mb-1">High Priority / Duplicates</h2>
          <p className="text-3xl text-purple-400">{metrics.high_priority_count} / {metrics.duplicate_count}</p>
          <p className="text-xs text-gray-500 mt-2">Requires immediate attention</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cash Flow Chart */}
        <div className="bg-surface rounded-lg p-4 shadow-md lg:col-span-2">
          <h2 className="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">30-Day Cash Flow Impact</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={cashflow}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" tick={{fontSize: 12}} tickFormatter={(val) => val.substring(5)} />
                <YAxis stroke="#9CA3AF" tick={{fontSize: 12}} />
                <Tooltip contentStyle={{backgroundColor: '#1F2937', borderColor: '#374151'}} />
                <Line type="monotone" dataKey="amount" stroke="#14B8A6" strokeWidth={3} dot={{r: 4}} activeDot={{r: 8}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Due Date Tracking List */}
        <div className="bg-surface rounded-lg p-4 shadow-md">
          <h2 className="text-xl font-semibold mb-4 border-b border-gray-700 pb-2">Due Date Tracking</h2>
          <div className="overflow-y-auto h-64 pr-2 space-y-3">
            {invoices.length === 0 ? (
              <p className="text-gray-400 text-sm">No active invoices.</p>
            ) : (
              invoices
                .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
                .slice(0, 15) // Show top 15 soonest
                .map(inv => (
                <div key={inv.id} className="flex justify-between items-center bg-gray-800 p-3 rounded-lg border border-gray-700">
                  <div>
                    <p className="font-semibold text-sm truncate w-32" title={inv.vendor_name}>{inv.vendor_name}</p>
                    <p className="text-xs text-gray-400">{inv.due_date}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">${inv.amount}</p>
                    <div className="mt-1">{getStatusBadge(inv)}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
