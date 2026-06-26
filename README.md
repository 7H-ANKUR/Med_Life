# 🏥 Travel Health Finder

> **Find the right doctor, right now — wherever you are in India.**

A location-aware medical recommendation web app for travelers. Describe your symptoms → AI identifies specialist + urgency → Google Maps finds nearby hospitals/clinics → ranked results with fee estimates and one-tap navigation.

---

## ✨ Features

- 🔍 **AI Symptom Analysis** — OpenAI / Gemini classifies symptoms to specialist + urgency (low / moderate / high / emergency)
- 🗺️ **Google Maps Powered** — Real-time nearby search with no static database
- 🚨 **Emergency Mode** — Detects emergencies, shows nearest open ER + Call 112 button
- 💰 **Fee Estimates** — City-specific consultation fee ranges from real data
- 🔖 **Save Places** — Bookmark hospitals for quick future access
- 📱 **Mobile-First** — Designed for travelers on phones

---

## 🏗️ Architecture

```
travel-health-finder/
├── apps/
│   ├── web/          ← Next.js 14 frontend (TypeScript + Tailwind)
│   └── api/          ← FastAPI backend (Python 3.11)
├── packages/
│   └── shared-types/ ← Shared TypeScript types
├── scripts/          ← ETL + seed scripts
└── docker-compose.yml
```

---

## 🚀 Quick Start

### Prerequisites
- Node 20+, Python 3.11+, Docker Desktop

### Step 1 — Google Cloud Setup (Required)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project `travel-health-finder`
3. Enable APIs: **Maps JavaScript API**, **Places API**, **Geocoding API**, **Directions API**
4. Create 2 API keys:
   - `BACKEND_MAPS_KEY` → restrict to server IP
   - `FRONTEND_MAPS_KEY` → restrict to HTTP referrer `localhost:3000`
5. Set billing alert at ₹2,000/month

### Step 2 — AI API Key

- **OpenAI:** [platform.openai.com](https://platform.openai.com) → API Keys → `sk-...`
- **Gemini (Free tier):** [aistudio.google.com](https://aistudio.google.com) → Get API Key

---

### Step 3 — Backend Setup

```bash
cd apps/api

# Create virtual environment
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and edit env file
copy ..\..\\.env.example .env
# Edit .env — add GOOGLE_MAPS_API_KEY and OPENAI_API_KEY
```

### Step 4 — Start Database

```bash
# From project root
docker compose up -d

# Verify it's running
docker compose ps
```

### Step 5 — Run Migrations + Seed

```bash
cd apps/api

# Create all 8 tables
alembic upgrade head

# Seed cities + parse fee data from dataset
cd ../..
python scripts/seed-db.py
```

### Step 6 — Start Backend

```bash
cd apps/api
uvicorn main:app --reload --port 8000

# API docs: http://localhost:8000/docs
# Health:   http://localhost:8000/health
```

### Step 7 — Frontend Setup

```bash
cd apps/web

# Copy env
copy .env.local.example .env.local   # or copy from .env.example
# Edit: add NEXT_PUBLIC_GOOGLE_MAPS_KEY

# Install and run
npm install
npm run dev
# App: http://localhost:3000
```

---

## 🔑 Environment Variables

### Backend (`apps/api/.env`)
| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL async connection string |
| `GOOGLE_MAPS_API_KEY` | ✅ | Backend Maps key (server-only) |
| `OPENAI_API_KEY` | ✅* | OpenAI key (*or use Gemini) |
| `GEMINI_API_KEY` | ✅* | Gemini key (*or use OpenAI) |
| `AI_PROVIDER` | ✅ | `openai` or `gemini` |
| `JWT_SECRET` | ✅ | 64-char random string |

### Frontend (`apps/web/.env.local`)
| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend URL (e.g. `http://localhost:8000/v1`) |
| `NEXT_PUBLIC_GOOGLE_MAPS_KEY` | ✅ | Frontend Maps key (referrer-restricted) |

---

## 🗺️ Google Maps Integration

All Maps calls go through the **backend proxy** — the backend key is never sent to the browser.

| API Used | Purpose |
|---|---|
| Places Nearby Search | Find hospitals/clinics/pharmacies |
| Place Details | Full hours, phone, reviews |
| Geocoding | City name → lat/lng |
| Maps JavaScript API (frontend) | Interactive map embed |
| Static Maps API (frontend) | Map preview on results page |
| Navigate deeplink | `maps.google.com/dir/?api=1&destination=place_id:XXX` |

---

## 🧪 Testing

```bash
# Backend unit tests
cd apps/api
pytest tests/ -v

# Frontend build check
cd apps/web
npm run build

# Type check
npm run lint
```

---

## 🚢 Deployment

### Frontend → Vercel
```bash
cd apps/web
npx vercel --prod
# Set env vars in Vercel dashboard
```

### Backend → Render
1. Connect GitHub repo → New Web Service → `apps/api`
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
4. Add all env vars in Render dashboard

### Database → Render Postgres or Supabase
- After deploy, run: `alembic upgrade head` via Render Shell
- Then: `python scripts/seed-db.py`

---

## 📂 Key Files

| File | Purpose |
|---|---|
| [`apps/api/services/maps_service.py`](apps/api/services/maps_service.py) | Google Maps proxy service |
| [`apps/api/services/ai_service.py`](apps/api/services/ai_service.py) | OpenAI/Gemini symptom analysis |
| [`apps/api/services/ranking_service.py`](apps/api/services/ranking_service.py) | Scoring engine (normal + emergency mode) |
| [`apps/api/services/fee_service.py`](apps/api/services/fee_service.py) | Fee estimation from dataset |
| [`apps/api/routers/places.py`](apps/api/routers/places.py) | Core nearby search endpoint |
| [`apps/web/src/app/search/page.tsx`](apps/web/src/app/search/page.tsx) | Symptom search page |
| [`apps/web/src/app/results/page.tsx`](apps/web/src/app/results/page.tsx) | Results + map view |
| [`apps/web/src/app/emergency/page.tsx`](apps/web/src/app/emergency/page.tsx) | Emergency page |
| [`scripts/parse-fee-dataset.py`](scripts/parse-fee-dataset.py) | ETL from docter.csv |

---

## ⚠️ Medical Disclaimer

This app provides guidance only. It is **not a substitute for professional medical advice**. In an emergency, **call 112** immediately.

---

## 🌐 Deployment

### Backend (Render)

This project includes a `render.yaml` for automatic deployments to [Render](https://render.com/).

1. Create a Render account and connect your GitHub.
2. Go to the Dashboard → **Blueprints** → **New Blueprint Instance**.
3. Select this repository. Render will automatically detect the FastAPI backend.
4. Fill in the required environment variables:
   - `DATABASE_URL` (Your Supabase Postgres connection string)
   - `GOOGLE_MAPS_API_KEY`
   - `GEMINI_API_KEY` (or `OPENAI_API_KEY`)
   - `JWT_SECRET` (A strong random string)

### Frontend (Vercel)

1. Create a [Vercel](https://vercel.com/) account and connect your GitHub.
2. Click **Add New** → **Project** and select this repository.
3. Configure the Project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web`
4. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`: Your deployed Render backend URL (e.g., `https://travel-health-api.onrender.com/v1`)
   - `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`: Your Maps API Key
5. Click **Deploy**.

---

## 📄 License

MIT

---

## 📄 Documentation

All design documents are in the `med/` project root:
- `01-product-requirements.md` — Full PRD
- `04-system-architecture.md` — System components
- `06-api-contracts.md` — API reference
- `08-scoring-engine-spec.md` — Ranking logic
- `10-development-phases.md` — 8-week roadmap
