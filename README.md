# Finance Operations Copilot  
*A lightweight AI‑augmented demo for automating invoice & receivable workflows.*

---  

## 📖 Project Overview  
Finance Operations Copilot (aka **Finance‑Copilot**) is a full‑stack demo that shows how generative AI (Gemini) can be woven into a classic back‑office process: ingesting invoices, extracting key fields, classifying vendors, computing a payment priority score, and managing receivables.  

The repository contains:

| Layer | Technology | Description |
|-------|------------|-------------|
| **Backend** | FastAPI + SQLAlchemy + SQLite | REST API exposing invoice & receivable endpoints. |
| **Frontend** | Vite + React (JSX) + Tailwind‑free CSS | Interactive UI for uploading invoices/receivables and visualising AI‑generated insights. |
| **AI utils** | `gemini_vision.py`, `vendor_classify.py`, `priority.py` | Minimal stubs that call Gemini (or mock) to perform OCR, classification and scoring. |

All components run locally; no external services besides the Gemini API are required.  

---  

## 🎯 Problem Statement  
Finance teams spend countless hours manually:  

* Scanning invoices, extracting dates, amounts, and vendor names.  
* Classifying vendors to apply payment terms or risk policies.  
* Prioritising payments based on due dates, amounts, and vendor risk.  

These tasks are repetitive, error‑prone, and hinder cash‑flow optimisation.  

**Finance Operations Copilot** demonstrates how a single AI‑driven “copilot” can automate this pipeline while keeping the codebase simple and extensible.  

---  

## 💼 Business Value  

### Accounts Payable  

* Reduce manual invoice processing effort  
* Prioritize payments based on urgency and business impact  
* Improve cash‑flow visibility  

### Accounts Receivable  

* Identify high‑priority collections  
* Accelerate customer follow‑ups  
* Reduce overdue receivables through AI‑generated reminders  

---  

## ✨ Key Features  

| Feature | Description |
|---------|-------------|
| **Invoice upload** | Drag‑and‑drop PDF/JPG/PNG → stored on disk. |
| **AI OCR extraction** | Calls `gemini_vision.extract_invoice()` to pull `invoice_number`, `vendor_name`, `invoice_date`, `due_date`, `amount`, `currency`. |
| **Vendor classification** | `vendor_classify.classify_vendor()` returns a category + reasoning. |
| **Priority scoring** | `priority.calculate_priority()` combines due date, vendor risk and amount → numeric score + recommendation. |
| **Duplicate detection** | Simple invoice‑number + vendor check. |
| **Receivable management** | Bulk JSON upload, priority calc, email‑draft generation. |
| **Live dashboard** | React UI shows extracted data, classification, priority and email draft in clean cards. |
| **Auto DB creation** | SQLite tables (`invoices`, `receivables`) created on FastAPI startup. |

---  

## 🏗️ Architecture (ASCII)  

```
+-------------------+          +-------------------+          +-------------------+
|   Frontend (Vite) |  <--->   |   Backend (FastAPI)  <--->   |   SQLite DB      |
|   React UI        |          |   /app            |          |   finance.db      |
|   InvoiceUpload   |          |   - routers/      |          |   - invoices      |
|   ReceivableDash  |          |       invoice.py |          |   - receivables   |
|   Dashboard etc.  |          |       receivable.py|        +-------------------+
+-------------------+          |   - utils/       |
                               |       gemini_vision.py  (calls Gemini) |
                               |       vendor_classify.py (AI) |
                               |       priority.py       (logic)   |
                               +-------------------+
```

---  

## 🛠️ Tech Stack  

| Layer | Tech | Version (as of repo) |
|-------|------|----------------------|
| **API** | FastAPI | 0.115 |
| **ORM** | SQLAlchemy | 2.0 |
| **Server** | Uvicorn | 0.30 |
| **DB** | SQLite (file `finance.db`) | — |
| **Frontend** | Vite (dev server) | ^8.0.12 |
| **JS Framework** | React (JSX) | ^18 |
| **Styling** | Vanilla CSS (dark‑mode, glassmorphism) | — |
| **AI** | Google Gemini (via `google-generativeai`) | — |
| **Python** | 3.12 | — |

---  

## 🤖 AI Workflow Explanation  

```
[Upload] → FastAPI saves file → gemini_vision.extract_invoice()
   ↓
Extracted fields stored in `Invoice` row
   ↓
vendor_classify.classify_vendor(vendor_name) → category + reasoning
   ↓
priority.calculate_priority(due_date, vendor_category, amount, risk_notes)
   → score + recommendation
   ↓
All results returned to the frontend in a single UI flow.
```

*Each AI call is encapsulated in the `utils/` package, making future swaps (e.g., another LLM) trivial.*

---  

## 📚 API Endpoints  

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| **POST** | `/invoice/upload` | Store file & create `Invoice` entry | `multipart/form-data` (`file`) | `{message, invoice_id}` |
| **GET** | `/invoice/{id}/extract` | Run OCR (if not already) & return fields | – | `InvoiceExtractResponse` |
| **GET** | `/invoice/{id}/classify` | Classify vendor using Gemini | – | `VendorClassificationResponse` |
| **GET** | `/invoice/{id}/priority` | Compute priority score | – | `PriorityScoreResponse` |
| **GET** | `/invoice/{id}/duplicate` | Simple duplicate detection | – | `{duplicate: true/false}` |
| **POST** | `/receivable/upload` | Bulk upload list of receivables | JSON array of `ReceivableCreate` | `{message, count}` |
| **GET** | `/receivable/{id}/priority` | Compute priority for a receivable | – | `{priority_score}` |
| **GET** | `/receivable/{id}/email` | Generate reminder email draft | – | `EmailDraftResponse` |
| **GET** | `/health` | Liveness probe | – | `{status:"ok"}` |

*All request / response models are defined in `backend/app/schemas.py`.*

---  

## ⚙️ Setup Instructions  

### 1. Clone the repo  

```bash
git clone https://github.com/your‑org/finance‑copilot.git
cd finance-copilot
```

### 2. Backend  

```bash
# (optional) create a virtual env
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Environment variables (see below)
export DATABASE_URL="sqlite:///./finance.db"   # default, can be omitted

# Run the API (auto‑creates tables on startup)
uvicorn backend/app.main:app --reload
# API available at http://localhost:8000
```

### 3. Frontend  

```bash
cd src   # repository root contains the Vite project
npm install
npm run dev
# UI available at http://localhost:5173
```

---  

## 🔐 Environment Variables  

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy connection string. SQLite lives next to `backend/app`. | `sqlite:///./finance.db` |
| `GEMINI_API_KEY` | Gemini API key (required for real OCR / classification). | *must be set* |
| `UPLOAD_DIR` *(internal)* | Directory for uploaded files (`backend/uploads`). | Auto‑created |  

Create a `.env` file in `backend/` (or export manually) if you wish to override defaults.

---  

## 🚀 Running the Application  

| Component | Command | URL |
|-----------|---------|-----|
| **Backend** | `uvicorn backend/app.main:app --reload` | `http://localhost:8000` |
| **Frontend** | `npm run dev` (from repo root) | `http://localhost:5173` |

The UI automatically talks to the backend on `http://localhost:8000`.  

---  

## 🎬 Demo Scenarios  

1. **Invoice Flow**  
   *Navigate to “Upload Invoice”, select a PDF/JPG.*  
   - The file is saved under `backend/uploads`.  
   - The UI shows **Extracted Data** (invoice #, vendor, dates, amount).  
   - Immediately after extraction, the UI displays **Vendor Classification** (category + reasoning).  
   - Finally a **Priority Score** card appears with numeric score & recommendation.  

2. **Receivable Flow**  
   *POST a JSON array to `/receivable/upload` (e.g., via Postman or curl).*  

   ```json
   [
     {"customer":"Acme Corp","amount_due":1200.5,"days_overdue":45},
     {"customer":"Beta LLC","amount_due":320.0,"days_overdue":10}
   ]
   ```  

   - The API returns `{message:"Receivables uploaded", count:2}`.  
   - GET `/receivable/1/priority` returns a score (`amount_due * days_overdue`).  
   - GET `/receivable/1/email` returns a mock reminder email.  

---  

## 📌 Key Assumptions  

* SQLite is sufficient for a proof‑of‑concept; production would use a managed RDBMS.  
* The AI utilities (`gemini_vision`, `vendor_classify`) are stubs that call the Gemini API; they return deterministic mock data if the key is missing.  
* No authentication/authorization – the demo runs in a trusted environment.  
* Uploaded files are stored on the local filesystem; no cloud storage integration.  

---  

## ⚠️ Known Limitations  

| Limitation | Impact |
|------------|--------|
| **No auth** | Anyone with network access can call the API. |
| **Static priority logic** | Simple `amount * days_overdue` – does not consider cash‑flow constraints or dynamic business rules. |
| **Mock AI** | If `GEMINI_API_KEY` is not provided, the utils return placeholder values. |
| **Single‑process SQLite** | Concurrency is limited; heavy load may cause lock contention. |
| **Hard‑coded CORS** | `allow_origins=["*"]` is insecure for production. |
| **No validation of OCR output** | Incorrect data formats raise SQLite errors (now fixed for dates). |
| **No pagination / filtering** | Endpoints return only single records. |  

---  

## 🚀 Future Improvements  

* **Authentication** – integrate Firebase Auth or OAuth2.  
* **Production DB** – migrate to PostgreSQL / Cloud SQL and use Alembic migrations.  
* **Improved AI pipelines** – real Gemini Vision OCR, fine‑tuned vendor classification models, and a fully‑featured priority engine (consider cash‑flow optimisation).  
* **Background tasks** – move OCR & classification to Celery / FastAPI background tasks for non‑blocking uploads.  
* **File storage** – switch to S3 or GCS for scalable, secure uploads.  
* **UI polish** – add dark‑mode toggle, progress spinners, and more sophisticated dashboards (charts, filters).  
* **Testing** – unit & integration tests for all routers, plus CI pipeline.  
* **Docker / Kubernetes** – containerise backend and frontend for easy deployment.  

---  

## 💡 Key Technical Decisions  

* **FastAPI** was selected for its high‑performance async capabilities, automatic OpenAPI documentation, and excellent Python type‑safety—ideal for rapid prototyping of data‑centric services.  
* **SQLite** provides a zero‑configuration, file‑based database that lets the demo ship with a single `finance.db` file. This choice favours speed of iteration over scalability; a production system would swap in a managed RDBMS.  
* **Gemini** (Google’s multimodal LLM) was chosen because it offers both text generation and vision‑based OCR in a single API, minimizing the number of external services needed for a demo.  
* **Modular utils layer** (`utils/`) isolates AI calls from business logic, making the codebase easier to test, replace, or extend (e.g., swapping Gemini for another provider).  
* **Transparent rule‑based priority engine** keeps the scoring logic explicit and explainable, which is important for finance stakeholders who need to audit why a payment is marked high‑priority.  

---  

## 📈 What I Would Build Next  

* **Authentication & role‑based access** – secure the API and UI; separate finance, manager, and auditor roles.  
* **ERP integrations** – connectors for SAP, NetSuite, Zoho Books to pull/push invoices and receivables automatically.  
* **Cash‑flow forecasting** – predictive models that use historic payment patterns to forecast short‑term liquidity.  
* **AI‑driven payment‑scheduling recommendations** – suggest optimal payment dates that balance discounts, supplier relationships, and cash position.  
* **Bulk processing & background jobs** – queue large invoice batches, run OCR/classification asynchronously, and provide status feeds.  
* **Analytics dashboards & reporting** – KPI visualisations (DSO, payment‑lead time, overdue trends) with exportable reports.  

---  

## 👤 My Role  

* Designed the overall system architecture (API, DB, AI utilities, UI).  
* Built the React frontend, including the full upload‑extract‑classify‑priority flow.  
* Developed the FastAPI backend, data models, and route handlers.  
* Integrated Gemini AI workflows (OCR, vendor classification) via reusable utility modules.  
* Designed the rule‑based payment‑priority and receivable‑priority algorithms.  
* Debugged data‑type issues, added automatic DB creation, and delivered a complete end‑to‑end prototype within the assignment timeline.  

---  

## 📄 License  

This project is provided under the **MIT License** – feel free to fork, experiment, and adapt for your own internal demos.  
