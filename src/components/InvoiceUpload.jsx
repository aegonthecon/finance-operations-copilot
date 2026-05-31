// src/components/InvoiceUpload.jsx
import React, { useState } from "react";
import axios from "axios";

export default function InvoiceUpload() {
  const [file, setFile] = useState(null);
  const [uploadMsg, setUploadMsg] = useState("");
  const [extracted, setExtracted] = useState(null);
  const [classification, setClassification] = useState(null);
  const [priorityInfo, setPriorityInfo] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const uploadInvoice = async () => {
    if (!file) {
      setUploadMsg("Please select a file.");
      return;
    }
    const form = new FormData();
    form.append("file", file);
    try {
      const resp = await axios.post("http://localhost:8000/invoice/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const invoiceId = resp.data.invoice_id;
      setUploadMsg(`Uploaded, id ${invoiceId}. Extracting...`);
      // Trigger extraction
      const extractResp = await axios.get(`http://localhost:8000/invoice/${invoiceId}/extract`);
      const extractedData = extractResp.data;
      setExtracted(extractedData);
      // Classification
      const classifyResp = await axios.get(`http://localhost:8000/invoice/${invoiceId}/classify`);
      setClassification(classifyResp.data);
      // Priority
      const priorityResp = await axios.get(`http://localhost:8000/invoice/${invoiceId}/priority`);
      setPriorityInfo(priorityResp.data);
      setUploadMsg("Extraction, classification, and priority complete.");
    } catch (err) {
      setUploadMsg("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-4">
      <h2 className="text-2xl font-bold mb-2">Upload Invoice</h2>
      <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleFileChange} className="file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary/80" />
      <button onClick={uploadInvoice} className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/80 transition">
        Upload & Extract
      </button>
      {uploadMsg && <p className="mt-2 text-sm text-gray-300">{uploadMsg}</p>}
      {extracted && (
        <div className="mt-4 bg-surface p-4 rounded shadow-md">
          <h3 className="text-xl font-semibold mb-2">Extracted Data</h3>
          <pre className="whitespace-pre-wrap">{JSON.stringify(extracted, null, 2)}</pre>
        </div>
      )}
      {classification && (
        <div className="mt-4 bg-surface p-4 rounded shadow-md">
          <h3 className="text-xl font-semibold mb-2">Vendor Classification</h3>
          <p><strong>Category:</strong> {classification.category}</p>
          <p><strong>Reasoning:</strong> {classification.reasoning}</p>
        </div>
      )}
      {priorityInfo && (
        <div className="mt-4 bg-surface p-4 rounded shadow-md">
          <h3 className="text-xl font-semibold mb-2">Priority Score</h3>
          <p><strong>Score:</strong> {priorityInfo.priority_score}</p>
          <p><strong>Recommendation:</strong> {priorityInfo.recommendation}</p>
        </div>
      )}
    </div>
  );
}
