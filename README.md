# RYT Sports Academy · Football Academy Operating System (FAOS)

FAOS is the operating-system backend for RYT Sports Academy: a single platform for academy administration, player development, football operations, fees and finance, sponsors and funding, NPO governance, camps, merchandise, communications and AI-assisted workflows.

The project is built with **FastAPI + SQLAlchemy** and runs locally on SQLite by default. The database layer is environment-driven so the same code can later move to PostgreSQL.

## What is implemented

- One authoritative database (`academy.db` locally) instead of the former duplicate `academy_crm.db` path.
- Non-destructive additive migration for old SQLite databases.
- Core typed CRM API for players, parents, coaches, sponsors, funding, compliance, proposals, tournaments, fees, trials, attendance, messages, products and camps.
- Full FAOS data model based on `DATABASE_SPECIFICATION.md`, covering more than 50 resources across:
  - academy/teams;
  - football operations and player development;
  - finance;
  - sponsorship and grant funding;
  - governance/NPO administration;
  - commercial operations and camps;
  - AI conversations, proposals, reports and recommendations.
- Generic `/faos` administration CRUD API for the complete model set.
- Persistent sponsor CRUD (replaces the old in-memory sponsor demo).
- AI task router endpoint (`/chat`).
- WhatsApp message queue endpoints ready for a future Meta/Twilio transport.
- Existing proposal, funding and NPO helper modules retained.
- Browser dashboard served by the API at `/dashboard/`.
- Swagger `/docs`, ReDoc `/redoc`, `/health`, automated tests and GitHub Actions CI.
- Idempotent RYT seed command for the academy record and U9/U10/U13/U15/U17/U19 teams.

## Windows CMD setup

From the repository directory:

```cmd
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python scripts\migrate_db.py
python scripts\seed_ryt.py
start.bat
```

The seed command can be run again safely; it does not duplicate the academy or existing age-group teams.

Open:

- Dashboard: `http://127.0.0.1:8000/dashboard/`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

The migration command is safe for the legacy SQLite database: it creates missing tables and **adds** missing columns such as `parents.email`, `fees.due_date`, `trials.notes`, and `tournaments.location`. It does not drop your existing data.

## Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/migrate_db.py
python scripts/seed_ryt.py
./start.sh
```

## Configuration

Copy `.env.example` to `.env` if you want explicit configuration. Environment variables are read by the process; load the file with your preferred environment manager or set variables before starting the app.

Key settings:

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///academy.db` |
| `CORS_ORIGINS` | Comma-separated allowed browser origins | local development origins |
| `FAOS_API_KEY` | Optional protection for `/faos` write operations | unset |
| `OPENAI_API_KEY` | Reserved for future real AI-provider integration | unset |
| `WHATSAPP_ACCESS_TOKEN` | Reserved for Meta WhatsApp transport | unset |
| `WHATSAPP_PHONE_NUMBER_ID` | Reserved for Meta WhatsApp transport | unset |

If `FAOS_API_KEY` is configured, POST/PATCH/DELETE requests under `/faos` must include:

```text
X-API-Key: <your key>
```

## API structure

### Core CRM

Typed day-to-day academy routes live under `/crm`.

Examples:

```text
GET  /crm/summary
POST /crm/parents
POST /crm/players
POST /crm/sponsors
GET  /crm/sponsors
GET  /crm/sponsors/{id}
PATCH /crm/sponsors/{id}/status
DELETE /crm/sponsors/{id}
POST /crm/fees
POST /crm/trials
POST /crm/attendance
POST /crm/camps
```

Singular compatibility routes such as `/crm/sponsor`, `/crm/player`, `/crm/fee`, `/crm/trial` and `/crm/tournament` are retained for older clients.

### Full FAOS administration

The full database specification is available through a generic resource API:

```text
GET    /faos/resources
GET    /faos/{resource}
POST   /faos/{resource}
GET    /faos/{resource}/{id}
PATCH  /faos/{resource}/{id}
DELETE /faos/{resource}/{id}
```

Example resources include `organizations`, `teams`, `training_sessions`, `matches`, `player_statistics`, `expenses`, `bank_accounts`, `sponsor_contacts`, `grant_applications`, `directors`, `policies`, `orders`, `registrations`, `ai_conversations` and `player_insights`.

### AI and communications

```text
POST /chat
POST /whatsapp/send
GET  /whatsapp/queue
```

`/chat` currently uses the repository's rule-based routing engine. `/whatsapp/send` queues messages only; it does **not** send real WhatsApp messages until a Meta WhatsApp Business API or Twilio transport is connected.

## Architecture

```text
Browser dashboard
      |
      v
FastAPI server
  |-- /crm   -> typed academy workflows
  |-- /faos  -> complete FAOS resource CRUD
  |-- /chat  -> AI task router
  |-- /whatsapp -> communication queue
  |-- helper modules (funding / proposals / NPO)
      |
      v
Single SQLAlchemy Base + SessionLocal
      |
      v
SQLite (local) / PostgreSQL (future deployment)
```

The old `ai_agent.crm.database` module remains only as a compatibility re-export. It no longer creates a separate database.

## Database design

`DATABASE_SPECIFICATION.md` remains the design source of truth. The implemented model layer preserves older MVP columns where necessary so existing records continue to work while the expanded FAOS schema is added around them.

For SQLite development, `init_db()` performs additive upgrades automatically at application startup. For a production PostgreSQL deployment, introduce formal versioned migrations (for example Alembic) before any destructive or data-transforming schema change.

## Tests

```cmd
python -m pytest -q
```

The smoke suite validates:

- API startup and health;
- full FAOS resource registry;
- organization CRUD;
- parent → player → fee → trial workflow;
- sponsor create/list/update/delete persistence;
- CRM summary;
- dashboard serving.

GitHub Actions also runs `compileall` and the same test suite on pushes and pull requests.

## Production roadmap

The repository is now a runnable FAOS foundation. The remaining work is integration/production work rather than basic project wiring:

1. Move hosted deployments from SQLite to PostgreSQL.
2. Add user authentication, roles and permissions before exposing admin APIs publicly.
3. Add Alembic versioned migrations for production schema evolution.
4. Connect Meta WhatsApp Business API or Twilio for actual message delivery.
5. Connect an AI provider for generated proposals/reports/recommendations; keep human approval for external communications.
6. Add document/file storage for NPO documents, player documents and grant attachments.
7. Add automated database backups and audit logging.
8. Expand the dashboard into role-specific views for academy admin, coaches, parents and finance/governance users.

## Scope note

FAOS supports administration and decision-making. Legal, financial, compliance and AI-generated material should be reviewed by the appropriate responsible person before it is filed, signed, submitted or sent externally.
