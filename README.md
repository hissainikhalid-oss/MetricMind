# MetricMind

### Governed Semantic Business Intelligence Engine

MetricMind is a conversational business intelligence platform that converts natural-language business questions into governed analytical queries.

Instead of allowing unrestricted SQL generation, MetricMind uses a centralized semantic layer containing approved business metrics, dimensions, and definitions. This makes analytical answers consistent, transparent, reproducible, and auditable.

---

## Project Objective

Traditional conversational BI systems can generate inconsistent metric definitions or unrestricted database queries.

MetricMind addresses this problem by introducing a governed semantic layer between the user and the analytical warehouse.

The workflow is:

Business Question  
→ Intent Detection  
→ Semantic Metric Resolution  
→ Governed Query Generation  
→ Analytics Warehouse  
→ Conversational Answer  
→ Audit Trail

---

## Key Features

- Natural-language business analytics
- Governed semantic metric layer
- Centralized metric definitions
- Parameterized analytical queries
- Query result limits
- Dynamic analytical visualizations
- Root-cause analysis
- Conversational responses
- Query transparency
- Audit logging
- Business KPI dashboard
- Governed metric explorer
- Responsive frontend interface

---

## Example Questions

MetricMind currently supports questions such as:

```text
What is our total revenue?
What is our total profit?
What is our profit margin?
What was European revenue in Q3 2026?
What was European profit margin in Q3 2026?
Show revenue by region
Show profit by category
Show revenue by product
How much did we spend on shipping?
How many orders do we have?
Why did European profit margin drop in Q3 2026?
```

---

## Architecture

```text
┌──────────────────────────────┐
│        Business User         │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│     MetricMind Frontend      │
│   Vite + JavaScript + Charts │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│        FastAPI Layer         │
│         /api/ask             │
└───────────────┬──────────────┘
                │
         Intent Detection
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌───────────────┐  ┌────────────────┐
│ Query Engine  │  │ Analysis Engine│
└───────┬───────┘  └───────┬────────┘
        │                   │
        ▼                   │
┌──────────────────────┐    │
│   Semantic Layer     │    │
│   metrics.yaml       │    │
└──────────┬───────────┘    │
           │                │
           └────────┬───────┘
                    ▼
          ┌─────────────────┐
          │ SQLite Warehouse│
          │     sales       │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │   Audit Trail   │
          └─────────────────┘
```

---

## Governed Semantic Layer

Metric definitions are stored centrally in:

```text
semantic/metrics.yaml
```

Examples include:

### Total Revenue

```sql
SUM(revenue)
```

### Total Profit

```sql
SUM(profit)
```

### Profit Margin

```sql
(SUM(profit) / NULLIF(SUM(revenue), 0)) * 100
```

### Total Orders

```sql
COUNT(DISTINCT order_id)
```

Because these definitions are centrally governed, MetricMind does not invent a new formula each time a question is asked.

---

## Query Governance

MetricMind applies several controls before executing analytical queries.

### Approved Metrics

Only metrics defined in the semantic layer can be queried.

### Approved Dimensions

Grouping is restricted to approved dimensions such as:

- Region
- Country
- Category
- Product
- Year
- Quarter
- Month

### Parameterized Filters

User-selected filters are passed as SQL parameters rather than directly inserted into SQL strings.

### Result Limits

Grouped analytical queries are limited to:

```text
20 results
```

Example:

```sql
SELECT
    product AS dimension,
    SUM(revenue) AS value
FROM sales
GROUP BY product
ORDER BY value DESC
LIMIT 20;
```

This prevents unrestricted large analytical result sets.

---

## Root-Cause Analysis

MetricMind includes deterministic multi-step analysis for business questions such as:

```text
Why did European profit margin drop in Q3 2026?
```

The analytical engine compares the requested quarter with the previous quarter and evaluates the major cost drivers.

Example result:

```text
Q2 2026 Profit Margin: 28.62%

Q3 2026 Profit Margin: 16.24%

Margin Change: -12.39 percentage points

Primary Driver: Material Cost
```

Cost contribution analysis:

```text
Material Cost: +9.94 pp
Shipping Cost: +2.45 pp
Operating Cost: approximately unchanged
```

The explanation is calculated directly from the analytical dataset rather than generated from unsupported assumptions.

---

## Dataset

MetricMind currently uses a reproducible synthetic corporate sales dataset designed for analytical demonstration.

Dataset size:

```text
6,000 transactions
```

Date range:

```text
January 2025 – September 2026
```

Example dimensions:

```text
Region
Country
Product
Category
Year
Quarter
Month
```

Example measures:

```text
Revenue
Profit
Material Cost
Shipping Cost
Operating Cost
Units Sold
```

An intentional cost increase was introduced into European Q3 2026 data to provide a measurable root-cause analysis scenario.

The dataset is synthetic and is not presented as real company data.

---

## Dashboard

The executive dashboard displays governed KPIs including:

- Total Revenue
- Total Profit
- Profit Margin
- Total Orders
- Revenue by Region
- Governed analytical insights

Current dataset totals include approximately:

```text
Revenue: $28.60M
Profit:  $8.03M
Margin:  28.07%
Orders:  6,000
```
---

## Conversational BI

MetricMind exposes a unified conversational analytics endpoint:

```http
POST /api/ask
```

Example request:

```json
{
  "question": "Show revenue by region"
}
```

Example response structure:

```json
{
  "mode": "governed_query",
  "success": true,
  "metric": "total_revenue",
  "governed": true,
  "filters": {},
  "group_by": "region",
  "results": []
}
```

The response can include:

- Conversational answer
- Governed metric
- Metric definition
- Filters
- Grouping dimension
- Generated SQL
- SQL parameters
- Query-governance metadata
- Analytical results

---

## API Endpoints

### Health Check

```http
GET /health
```

### Governed Metrics

```http
GET /api/metrics
```

### Semantic Dimensions

```http
GET /api/dimensions
```

### Governed Query

```http
POST /api/query
```

### Root-Cause Analysis

```http
POST /api/analyze
```

### Unified Conversational Analytics

```http
POST /api/ask
```

### Audit History

```http
GET /api/audit
```

FastAPI automatically provides interactive Swagger documentation at:

```text
/docs
```

---

## Audit Trail

Successful analytical questions are recorded in the MetricMind audit system.

The audit log records:

- Question
- Query mode
- Governed metric
- Filters
- Generated query
- Governance status
- Timestamp

This provides traceability and makes analytical activity auditable.

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pandas
- PyYAML
- SQLite

### Analytics

- Governed semantic metrics
- Deterministic intent detection
- Parameterized SQL generation
- Root-cause analysis
- Query governance

### Frontend

- Vite
- HTML
- CSS
- JavaScript
- Chart.js

### Data

- Reproducible synthetic corporate sales dataset
- SQLite analytical warehouse

---

## Project Structure

```text
MetricMind/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── semantic_engine.py
│   ├── query_engine.py
│   ├── analysis_engine.py
│   └── audit_service.py
│
├── data/
│   ├── generate_data.py
│   └── corporate_sales.csv
│
├── semantic/
│   └── metrics.yaml
│
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   └── package.json
│
├── tests/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd MetricMind
```

### 2. Create a Python virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

### 4. Generate the synthetic dataset

```powershell
python data\generate_data.py
```

### 5. Initialize and validate the analytical database

```powershell
python backend\database.py
```

### 6. Start the backend

```powershell
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Design Principles

### Consistency

The same business metric always resolves to the same centrally governed definition.

### Transparency

Metric definitions, generated analytical queries, filters, and governance controls can be inspected.

### Traceability

Successful analytical requests are recorded in an audit trail.

### Grounded Analytics

Root-cause explanations are calculated from the underlying analytical data instead of being generated from unsupported assumptions.

### Controlled Access

Users cannot submit arbitrary SQL through the conversational interface. Metric and dimension selection is restricted to the governed semantic model.

---

## Current Implementation Scope

MetricMind is currently an MVP implementation of governed conversational business intelligence.

The analytical warehouse currently uses:

```text
SQLite
```

The semantic layer is implemented using:

```text
Python + YAML
```

The conversational routing layer currently uses deterministic intent detection rather than a production LLM agent.

These choices make the current version reproducible, lightweight, and suitable for demonstrating the governed semantic BI architecture.

Potential enterprise extensions include:

```text
Snowflake / Databricks
dbt
Cube.dev
LangChain
Llama-based orchestration
Next.js
Enterprise authentication
Distributed query-cost monitoring
```

---

## Project Status

Implemented:

- Synthetic analytical dataset
- Analytical warehouse
- Governed semantic layer
- Governed metric definitions
- Natural-language metric resolution
- Region, year and quarter filtering
- Dynamic grouping
- Parameterized filters
- Query result limits
- Root-cause analysis
- Conversational responses
- FastAPI REST API
- Query transparency
- Query governance metadata
- Audit logging
- Executive KPI dashboard
- Dynamic charts
- Semantic governance interface
- Governed metric explorer
- Responsive frontend

---

## MetricMind

**Ask business questions. Get governed answers.**