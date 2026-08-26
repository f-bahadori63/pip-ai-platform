# PIP AI Platform

**Project Intelligence Platform for EPC Industries — MVP 1.0**

PIP is an AI-powered project management intelligence platform for EPC (Engineering, Procurement & Construction) and industrial projects. It transforms project files and operational data into structured project intelligence, analysis, alerts, reporting, and management decision-support outputs.

> **Current MVP priority:**
> `Upload → Validate → Parse → Extract → Analyze → Structured Result → UI`

---

## ✨ Highlights

- 📂 **Document intelligence** — upload Excel/PDF project files, validate, parse and extract project data
- 🗂️ **WBS & Scheduling** — work breakdown structure, schedule import *(with idempotency)*, critical path analysis, delay index and recovery plans
- 📄 **Contract intelligence** — contract capture, analysis and monitoring
- ⚠️ **Risk module** — risk register, AI risk assessment and prioritised reports
- 💰 **Cost intelligence** — cost KPIs and control indicators
- 📊 **Executive dashboard** — schedule control analytics and project control KPIs
- 🧠 **Local AI (Ollama)** — on-premise LLM inference (`qwen2.5:3b`), keeping sensitive EPC project data off the cloud

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, Alembic |
| Database | PostgreSQL 16 |
| Frontend | React 19, TypeScript, Vite, MUI |
| AI / Search | Ollama (local LLM), Qdrant (vector DB) |
| Storage & Queue | MinIO (S3), Redis, RabbitMQ |
| Infra | Docker Compose, pgAdmin |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### 1. Start the infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, RabbitMQ, Qdrant, MinIO, Ollama and pgAdmin
(ports: `5432`, `6379`, `5672`/`15672`, `6333`/`6334`, `9000`/`9001`, `11434`, `5050`).

### 2. Configure the backend

```bash
cp .env.example .env       # then edit values if needed
python -m venv .venv
.venv\Scripts\activate     # Windows  (use `source .venv/bin/activate` on Linux/macOS)
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
alembic upgrade head
```

### 4. Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: <http://localhost:8000/docs>

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: <http://localhost:5173>

---

## 📁 Project Structure

```
pip-ai-platform/
├── app/                    # FastAPI backend
│   ├── api/                # (reserved) API layer
│   ├── core/               # settings / config
│   ├── database/           # SQLAlchemy engine, sessions, Alembic migrations
│   ├── models/             # ORM models (project, contract, risk, wbs, schedule, cost)
│   ├── routers/            # API endpoints (projects, wbs, risks, contracts, schedule, ai, documents, ...)
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # business logic + AI services (Ollama client, analyzers, KPIs)
│   └── tests/
├── frontend/               # React 19 + TypeScript + Vite + MUI
├── docs/sprints/           # sprint documentation (01–07)
├── .ai/                    # project constitution, agents, knowledge
├── .artifacts/             # product/architecture/design documents (10 domains)
├── .devtools/              # ops scripts
├── compose.yaml            # local infrastructure stack
├── alembic.ini
└── requirements*.txt
```

---

## 🧩 Modules

| Module | Router | Status |
|---|---|---|
| Projects | `/projects` | ✅ |
| WBS | `/wbs` | ✅ |
| Contracts | `/contracts` | ✅ |
| Risks | `/risks`, `/risk-register` | ✅ |
| Schedule (import + control) | `/schedule`, `/schedule/import` | ✅ |
| Cost | `/cost` | ✅ |
| AI assistant | `/ai` | ✅ |
| Dashboard | `/dashboard` | ✅ |
| Documents | `/documents` | ✅ |

---

## 📚 Documentation

- Product & architecture docs: [`.artifacts/`](.artifacts/)
- Sprint reports: [`docs/sprints/`](docs/sprints/)
- Project constitution: [`.ai/PIP_CONSTITUTION.md`](.ai/PIP_CONSTITUTION.md)

---

## 🔒 Security Notes

- All credentials live in `.env` (see [`.env.example`](.env.example)) — never commit `.env`.
- AI inference runs fully on-premise via Ollama; project data is not sent to external services.

---

## 🤝 Contributing

1. Pick an issue or open a new one to discuss the change.
2. Branch from `main` (`feature/<name>`).
3. Ensure the CI checks pass (backend compile + import smoke test, frontend build).

---

## 📄 License

[MIT](LICENSE)

---

## 🇮🇷 فارسی

**پلتفرم هوشمند مدیریت پروژه برای صنایع EPC** — این پلتفرم فایل‌ها و داده‌های عملیاتی پروژه را به هوش ساختاریافته‌ی پروژه، تحلیل، هشدار، گزارش و خروجی‌های پشتیبان تصمیم‌گیری مدیریتی تبدیل می‌کند. هوش مصنوعی به‌صورت کاملاً محلی (Ollama) اجرا می‌شود تا داده‌های حساس پروژه‌های صنعتی به سرویس‌های ابری ارسال نشوند.

**مسیر اجرا:** `docker compose up -d` ← `pip install -r requirements.txt` ← `alembic upgrade head` ← `uvicorn app.main:app` ← `cd frontend && npm install && npm run dev`
