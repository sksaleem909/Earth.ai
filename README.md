# 🌍 TerraVision AI

### See Tomorrow. Build Smarter.

**TerraVision AI** is an AI-powered Urban Decision Intelligence Platform that helps governments, smart city authorities, and urban planners simulate infrastructure decisions before construction begins.

---

## ✨ Features

- **Scenario Builder** — Select city, project type, budget, and timeline to simulate infrastructure impact
- **AI Decision Engine** — 4 expert AI agents analyze every scenario from environmental, economic, traffic, and citizen perspectives
- **Interactive Maps** — OpenStreetMap integration with location selection and boundary drawing
- **Simulation Scores** — 10 key metrics including traffic, carbon, flood risk, green cover, and citizen happiness
- **Professional Reports** — Export detailed PDF reports with charts and recommendations
- **Analytics Dashboard** — Track trends across all simulations
- **AI Chat** — Ask natural-language questions about infrastructure decisions

---

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend
```bash
cd backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Login
- **Email:** admin@terravision.ai
- **Password:** Password123

---

## 🐳 Docker Start

```bash
docker-compose up --build
```

Access the app at http://localhost:5173

---

## 🏗 Architecture

```
TerraVision AI
├── frontend/          # React 19 + Vite + TypeScript
├── backend/           # FastAPI + SQLAlchemy
├── docker-compose.yml # Container orchestration
└── .env               # Environment configuration
```

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, TypeScript, Tailwind CSS, Recharts, React Leaflet, Framer Motion |
| Backend | FastAPI, SQLAlchemy, Pydantic, Python 3.12 |
| Database | SQLite (dev) / PostgreSQL + PostGIS (production) |
| AI | Google Gemini API (with intelligent mock fallback) |
| Auth | JWT (JSON Web Tokens) |

---

## 📄 License

MIT License — Built for innovation.
