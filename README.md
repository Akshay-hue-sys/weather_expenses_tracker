# 🌤️ Weather & Expense Tracker (Dual-Domain Service)

A production-style FastAPI application featuring **strict domain segregation** between a stateless live weather intelligence service and a persistent SQLite expense tracking ledger.

Served locally over **HTTPS (TLS)** with an interactive single-page dashboard.

---

## 🏛️ Architecture & Separation of Concerns

This project enforces two independent bounded contexts under a unified ASGI gateway:

1. **Weather Service (Stateless Domain):**
   - Connects to the **Open-Meteo Geocoding API** to resolve human location queries (cities, states, countries) into geographic coordinates.
   - Fetches live temperature, wind speed, and meteorological condition codes from the **Open-Meteo Forecast API**.
   - Translates raw WMO numeric weather codes into human-readable descriptions (e.g., Clear Sky, Light Rain).
   - Zero database footprint: does not touch or store expense records.

2. **Expense Tracker (Persistent Domain):**
   - Pure financial ledger storing `id`, `title`, `amount`, `category`, and `created_at`.
   - Persisted on disk using local **SQLite with Write-Ahead Logging (`WAL`)** mode for high-concurrency read efficiency.
   - Computes aggregated spending summaries and category breakdowns via SQL aggregation.
   - Zero external API dependencies: operates completely independent of weather services.

3. **Presentation Layer:**
   - Single-page application (`index.html`) mounted via FastAPI's `StaticFiles`.
   - Uses native browser `fetch()` API and structured CSS card layouts for real-time updates without page reloads.

---

## 🛠️ Tech Stack

- **Runtime & Package Manager:** Python 3.12+ managed with `uv`
- **Web Framework:** FastAPI (ASGI)
- **Data Validation:** Pydantic v2
- **Database:** SQLite (WAL mode enabled)
- **HTTP Client:** `httpx` (asynchronous)
- **Security:** Local TLS termination with `mkcert`

---

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have `uv` installed on your machine:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies

From the repository root:

```bash
uv sync
```

### 3. Generate Local TLS Certificates (Optional for HTTPS)

To run over secure HTTPS locally using `mkcert`:

```bash
mkcert -install
mkcert localhost 127.0.0.1 ::1
```

### 4. Run the Application

Start the Uvicorn ASGI server over HTTPS:

```bash
uv run python -m uvicorn projects.weather_expense_tracker.src.app:app --reload --port 8000 --ssl-keyfile localhost+1-key.pem --ssl-certfile localhost+1.pem
```

*Note: To run over plain HTTP instead, omit the `--ssl-*` flags.*

---

## 🧭 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Web Dashboard UI |
| `GET` | `/docs` | Interactive OpenAPI / Swagger UI |
| `GET` | `/weather` | Coordinate-based weather query (`latitude`, `longitude`) |
| `GET` | `/weather/search` | Location-name weather search (`location_name`) |
| `POST` | `/expenses` | Record a new expense (`title`, `amount`, `category`) |
| `GET` | `/expenses` | List all historical expenses |
| `GET` | `/expenses/summary` | Aggregate financial totals and category breakdown |

---

## 🔒 Security & Privacy Hygiene

- Local SQLite database files (`*.db`, `*.db-wal`) and private TLS certificates (`*.pem`, `*.key`) are strictly excluded via `.gitignore` to prevent credential exposure and repository bloat.