# 🛒 Retail360 — End-to-End Data Engineering Pipeline

A production-style retail data platform built with open-source tools.

## 🏗️ Architecture

Raw Data (CSV)
│
▼
Apache Airflow (Orchestration)
│
▼
PySpark (Batch Ingestion)
│
▼
PostgreSQL Data Warehouse
├── Bronze (raw)
├── Silver (cleaned)
└── Gold (aggregated)
│
▼
dbt (Transformations + Tests)
│
▼
Apache Superset (Dashboard)


## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Apache Airflow | Pipeline orchestration and scheduling |
| PySpark | Batch data ingestion |
| PostgreSQL | Data warehouse |
| dbt | SQL transformations |
| Apache Kafka | Real-time streaming |
| Great Expectations | Data quality checks |
| Apache Superset | Dashboard and reporting |
| Docker | Containerisation |

## 🚀 How to Run

**1. Clone the repo**

git clone https://github.com/YOUR_USERNAME/retail360-pipeline.git
cd retail360-pipeline


**2. Start all services**

docker compose up -d


**3. Generate sample data**

python ingestion/generate_data.py


**4. Open Airflow UI**

URL: http://localhost:8080
Username: admin
Password: admin


**5. Trigger the DAG** — `retail360_bronze_pipeline`

## 📁 Project Structure

retail360-pipeline/
├── airflow/
│ └── dags/
│ └── ecommerce_pipeline.py
├── ingestion/
│ ├── generate_data.py
│ └── spark_ingest.py
├── dbt_project/
├── docker/
│ └── init.sql
├── docker-compose.yml
├── .env
└── README.md


## 📊 Pipeline Phases

- [x] Phase 1 — Infrastructure (Docker + Postgres + Airflow + Kafka)
- [x] Phase 2 — Bronze Ingestion (PySpark)
- [ ] Phase 3 — Silver Transformations (dbt)
- [ ] Phase 4 — Gold Marts (dbt)
- [ ] Phase 5 — Data Quality (Great Expectations)
- [ ] Phase 6 — Dashboard (Apache Superset)
- [ ] Phase 7 — Streaming (Kafka)