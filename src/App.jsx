// src/App.jsx
import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import InvoiceUpload from "./components/InvoiceUpload";
import PaymentPriorities from "./components/PaymentPriorities";
import ReceivablesDashboard from "./components/ReceivablesDashboard";
import EmailGenerator from "./components/EmailGenerator";

const linkClass = "px-4 py-2 text-gray-200 hover:text-teal-300";

export default function App() {
  return (
    <div className="min-h-screen bg-background text-white flex flex-col">
      <header className="bg-surface p-4 shadow-md">
        <nav className="flex space-x-4">
          <NavLink to="/" end className={({ isActive }) => isActive ? "font-bold " + linkClass : linkClass}>Dashboard</NavLink>
          <NavLink to="/upload" className={({ isActive }) => isActive ? "font-bold " + linkClass : linkClass}>Invoice Upload</NavLink>
          <NavLink to="/priorities" className={({ isActive }) => isActive ? "font-bold " + linkClass : linkClass}>Payment Priorities</NavLink>
          <NavLink to="/receivables" className={({ isActive }) => isActive ? "font-bold " + linkClass : linkClass}>Receivables</NavLink>
          <NavLink to="/email" className={({ isActive }) => isActive ? "font-bold " + linkClass : linkClass}>Email Generator</NavLink>
        </nav>
      </header>
      <main className="flex-1 p-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<InvoiceUpload />} />
          <Route path="/priorities" element={<PaymentPriorities />} />
          <Route path="/receivables" element={<ReceivablesDashboard />} />
          <Route path="/email" element={<EmailGenerator />} />
        </Routes>
      </main>
      <footer className="bg-surface p-2 text-center text-gray-400 text-sm">
        Finance Operations Copilot © 2026
      </footer>
    </div>
  );
}
