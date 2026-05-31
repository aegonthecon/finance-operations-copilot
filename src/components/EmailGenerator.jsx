// src/components/EmailGenerator.jsx
import React, { useState } from "react";
import axios from "axios";

export default function EmailGenerator() {
  const [receivableId, setReceivableId] = useState("");
  const [email, setEmail] = useState(null);
  const [msg, setMsg] = useState("");

  const generate = async () => {
    if (!receivableId) {
      setMsg("Enter a receivable ID.");
      return;
    }
    try {
      const resp = await axios.get(`http://localhost:8000/receivable/${receivableId}/email`);
      setEmail(resp.data);
      setMsg("Email generated.");
    } catch (err) {
      setMsg("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-4">
      <h2 className="text-2xl font-bold mb-2">Generate Payment Reminder Email</h2>
      <input
        type="text"
        placeholder="Receivable ID"
        value={receivableId}
        onChange={(e) => setReceivableId(e.target.value)}
        className="w-full p-2 rounded bg-surface text-white"
      />
      <button onClick={generate} className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/80 transition">
        Generate Email
      </button>
      {msg && <p className="text-sm text-gray-300">{msg}</p>}
      {email && (
        <div className="mt-4 bg-surface p-4 rounded shadow-md">
          <h3 className="text-xl font-semibold mb-2">{email.subject}</h3>
          <pre className="whitespace-pre-wrap">{email.body}</pre>
        </div>
      )}
    </div>
  );
}
