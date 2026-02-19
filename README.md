# 🚀 BAAP AI — Database Analytics Platform
### The Baap Company · Business Applications and Platforms

AI-powered natural language database analytics. Ask questions in plain English, get SQL + charts + insights instantly.

---

## 📁 Project Structure

```
baap-ai/
├── backend/                         ← Python FastAPI
│   ├── main.py                      ← All API routes
│   ├── requirements.txt
│   ├── .env                         ← Add your GEMINI_API_KEY here
│   └── modules/
│       ├── db_connection.py         ← Module 1: Connect MySQL/PostgreSQL
│       ├── nl_to_sql.py             ← Module 2: English → SQL (Gemini)
│       ├── sql_executor.py          ← Module 3: Run SQL safely
│       ├── metrics_generator.py     ← Module 4: Stats (avg/min/max)
│       ├── visualization.py         ← Module 5: Auto chart config
│       ├── insight_generator.py     ← Module 6: AI insights (Gemini)
│       └── suggestion_generator.py  ← Module 7: Smart follow-up questions
│
└── frontend/                        ← Next.js 14
    ├── package.json
    └── src/
        ├── app/
        │   ├── page.tsx             ← Main app state
        │   ├── layout.tsx
        │   └── globals.css
        └── components/
            ├── ConnectPage.tsx      ← Screen 1: DB connection form
            ├── DashboardPage.tsx    ← Screen 2: Query + results
            ├── MetricCards.tsx      ← KPI cards (count/avg/max/min)
            ├── DataTable.tsx        ← Searchable, paginated table
            ├── ChartSection.tsx     ← Bar / Line / Pie charts
            └── InsightsSuggestions.tsx ← AI insights + next questions
```

---

## ⚙️ STEP-BY-STEP SETUP

---

### STEP 1 — Get Your Free Gemini API Key

1. Go to → https://aistudio.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy the key (looks like: `AIzaSy...`)

---

### STEP 2 — Setup Backend

**Open a terminal and run:**

```bash
# Go into backend folder
cd baap-ai/backend

# Create Python virtual environment (recommended)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

**Add your API key:**

Open the file `backend/.env` and replace the placeholder:

```env
GEMINI_API_KEY=AIzaSy_your_actual_key_here
```

**Start the backend:**

```bash
uvicorn main:app --reload --port 8000
```

✅ You should see: `Uvicorn running on http://127.0.0.1:8000`

Test it: Open http://localhost:8000 in browser → should show `{"message": "BAAP AI Backend is running ✓"}`

---

### STEP 3 — Setup Frontend

**Open a NEW terminal window and run:**

```bash
# Go into frontend folder
cd baap-ai/frontend

# Install Node.js dependencies
npm install

# Start the frontend dev server
npm run dev
```

✅ You should see: `Local: http://localhost:3000`

**Open http://localhost:3000 in your browser**

---

### STEP 4 — Connect & Use

1. **Fill in the connection form** (matches your screenshot exactly):
   - Database Driver: `mysql` or `postgresql`
   - Port: `3306` (MySQL) or `5432` (PostgreSQL)
   - Host: `localhost` (or your server IP)
   - Database Name: your database (e.g. `schools_data`)
   - Username: e.g. `root`
   - Password: your DB password

2. **Click "Connect to Database"**
   → If successful, moves to the Analytics Dashboard

3. **Type any question** in the AI Query Assistant:
   - `show the number of students per standard`
   - `what are the top 10 products by sales?`
   - `count records grouped by category`

4. **Click "Execute Query"** (or press Ctrl+Enter)
   → See: SQL query + metric cards + data table + chart + AI insights

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/connect` | Test connection + get schema |
| POST | `/api/query` | Full pipeline (NL→SQL→results) |
| POST | `/api/schema` | Get schema only |

### Example `/api/query` request:
```json
{
  "db_config": {
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "yourpassword",
    "database": "schools_data"
  },
  "question": "show the number of students per standard"
}
```

---

## 🔒 Security

- Only `SELECT` queries are allowed (no DROP, DELETE, INSERT, UPDATE, ALTER)
- Forbidden keywords are blocked with an error message
- Credentials stay server-side only — never sent to Gemini
- DB passwords are never logged

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + TypeScript |
| Styling | Tailwind CSS + inline styles |
| Charts | Chart.js + react-chartjs-2 |
| Backend | FastAPI (Python) |
| LLM | Google Gemini 1.5 Flash |
| MySQL | mysql-connector-python |
| PostgreSQL | psycopg2-binary |

---

## 🐛 Common Issues

**"Connection refused" on frontend:**
→ Make sure backend is running on port 8000: `uvicorn main:app --reload --port 8000`

**"GEMINI_API_KEY not set":**
→ Check your `backend/.env` file has the key correctly set

**MySQL connection error:**
→ Make sure MySQL is running: `mysql -u root -p`
→ Check host/port/credentials

**PostgreSQL connection error:**
→ Make sure PostgreSQL is running: `psql -U postgres`
→ Check `pg_hba.conf` allows local connections

**npm install fails:**
→ Make sure Node.js >= 18 is installed: `node --version`

---

## ✅ Requirements

- Python 3.9+
- Node.js 18+
- MySQL or PostgreSQL running locally or remotely
- Free Gemini API key from https://aistudio.google.com/app/apikey
