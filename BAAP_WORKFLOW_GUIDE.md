# BAAP AI - Complete Project Workflow Guide

This document explains the complete architecture and data flow of the BAAP AI (Database Analytics) project. It covers how the frontend communicates with the backend, how databases are connected, how files are uploaded, and how natural language queries are processed into actionable insights.

---

## 🏗️ 1. High-Level Architecture Overview

The system follows a modern client-server architecture:

- **Frontend**: Built with React (Next.js) and TypeScript. It handles user interactions, database connection forms, file uploads, and renders the analytics dashboard (charts, metrics, insights).
- **Backend**: Built with Python and FastAPI. It acts as the core engine that connects to databases, processes files, communicates with AI models (Gemini) to convert text to SQL, runs the queries, and generates insights and chart configurations.

---

## 🔌 2. How the Database Connection Works

The connection workflow is designed to be flexible, supporting direct database connections (MySQL, PostgreSQL) and quick file uploads (SQLite).

### **Flow A: Direct Database Connection**

1. **User Input:** On the `ConnectPage`, the user enters their database credentials (Host, Port, DB Name, Username, Password, and DB Driver: MySQL/PostgreSQL).
2. **API Call (`/api/connect`):** The frontend sends a `POST` request to the backend with these credentials.
3. **Backend Processing (`routes_upload.py -> db_loader.py`):**
   - The backend reads the config and establishes a connection using the appropriate driver (`mysql.connector` or `psycopg2`).
   - It runs a schema extraction script depending on the DB type (e.g., `SHOW TABLES` for MySQL, or querying `information_schema` for Postgres).
   - It captures table names, column names, data types, and row counts.
4. **Response:** The backend returns a `status: "connected"` along with the full database schema.
5. **Frontend State:** The frontend saves this connection configuration and the schema in its state, then routes the user to the Analytics Dashboard.

### **Flow B: File Upload (The SQLite "Fallback" Workflow)**

1. **User Action:** The user clicks "Upload CSV / Excel" and selects a file (CSV, Excel, PDF, or Docx). No explicit DB credentials are required.
2. **Configuration Fallback:** The frontend automatically creates a fallback database configuration pointing to a local SQLite database named `baap_quick_upload`.
3. **API Call (`/api/upload`):** The frontend sends the file and the fallback configuration via a `multipart/form-data` POST request.
4. **Backend Processing (`routes_upload.py`):**
   - The backend connects to (or creates) the `baap_quick_upload.db` SQLite file in the backend directory.
   - For **CSV/Excel**: It reads the file using Pandas, sanitizes the column names, creates a new table (named after the file), and inserts the data.
   - For **PDF/Docx**: It extracts the text and stores it in an `uploaded_documents` table specifically designed for unstructured data.
5. **Schema Update:** After a successful upload, the frontend calls the `/api/connect` endpoint again using the SQLite fallback config so it can fetch the newly updated schema (which now contains the uploaded file as a table).

---

## 💬 3. The Natural Language Query Workflow

Once the user is on the Dashboard and their database is connected, they can type questions in plain English. Here is exactly what happens when they hit "Send":

1. **User Query:** User types "Show me sales by region" in the Chat Interface.
2. **API Request (`/api/query`):** The frontend sends the user's question, along with the active database configuration.
3. **Database Connection:** The backend temporarily re-connects to the database using the provided configuration and fetches the schema again.
4. **NL to SQL Conversion (`sql_agent.py`):**
   - The backend sends a carefully crafted prompt to the LLM (Gemini).
   - The prompt contains the user's question, the database dialect (MySQL, Postgres, or SQLite), and the database schema.
   - The AI responds with the exact SQL query required.
5. **Query Execution (`sql_agent.py`):** The backend executes the generated SQL query directly on the connected database.
6. **Data Processing:** The returning rows and columns are converted into a list of dictionaries (JSON format).

### 🧠 4. Intelligence and Analytics Generation

Before sending the data back to the user, the backend passes the queried data through several "Intelligence Engines":

- **Metrics Engine (`metrics_engine.py`):** Analyzes the numerical columns in the result set to calculate KPIs like Sums, Averages, Min, Max, and Counts.
- **Chart Engine (`chart_generator.py`):** Determines the best way to visualize the data. It looks at the columns (e.g., if there's a date and a number, it will recommend a Line Chart or Bar Chart) and generates a structured chart configuration.
- **Insights Engine (`insight_generator.py`):** Uses the LLM again to read the data results and generate 3-4 bullet points of plain English business insights (e.g., "Region X is performing 20% better than Region Y").
- **Suggestions Engine (`suggestion_engine.py`):** Recommends 3 logical follow-up questions the user might want to ask next based on the current data and schema.

7. **Final Response:** The backend packages the SQL query, raw data, metrics, chart settings, insights, and suggestions into a single JSON response.
8. **Frontend Rendering:** The Dashboard receives this JSON. It displays the raw data in a Table, renders the charts using Recharts/Chart.js, displays the metric cards, and writes out the insights in the chat window.

---

## 📂 5. Directory Structure Breakdown

### Backend (`/backend/`)

- `main.py`: The entry point for the FastAPI server. Registers all routes.
- `config.py`: Loads environment variables (`.env`) and constructs database connection strings.
- `api/`: Contains the route definitions (`routes_connect.py`, `routes_upload.py`, `routes_chat.py`, `routes_visualize.py`).
- `ingestion/`: Handles getting data _in_.
  - `db_loader.py`: Connects to databases and extracts schemas.
  - `csv_loader.py`, `pdf_loader.py`, `docx_loader.py`: Parsers for file uploads.
- `core/`: Contains core orchestration logic and conversational memory stub (`memory.py`).
- `processing/`: Contains `sql_agent.py` which talks to Gemini to turn English into SQL.
- `intelligence/`: Contains engines that analyze data results to create insights, suggestions, and metrics.
- `visualization/`: Contains `chart_generator.py` which decides which chart type to render on the frontend.

### Frontend (`/frontend/src/`)

- `components/ConnectPage.tsx`: The initial screen where users connect DBs or upload files.
- `components/DashboardPage.tsx`: The main analytics view containing the chat, charts, and tables.
- `components/ChartSection.tsx`: Renders the visually appealing charts based on backend configurations.
- `components/MetricCards.tsx`: Displays the key performance indicators (KPIs).

---

## 🔑 Summary of the Magic

The core innovation of BAAP AI is the **Schema Injection** technique. The application never sends your entire database to the AI. Instead, it only sends the _Schema_ (table names and column names) to the AI to generate a SQL query. The SQL query is then executed securely on your local machine/server, ensuring your actual raw data remains private and secure.
