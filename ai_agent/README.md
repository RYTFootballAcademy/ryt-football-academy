# RYT Sports Academy FAOS · Application Package

`ai_agent` contains the Python application for the RYT Football Academy Operating System (FAOS). The root `README.md` is the primary setup and operations guide.

## Package map

```text
ai_agent/
  api/       FastAPI application entry point
  core/      deterministic academy decision router
  crm/       typed day-to-day academy CRM API and core models
  faos/      extended FAOS data model and generic administration API
  modules/   specialist helpers retained for sponsorship, NPO, funding,
             proposals, camps, commerce, communication and other workflows
```

## Current capabilities

- Academy, team, player, parent and coach records
- Attendance, training/match/development resources
- Fees, payments, budgets, income, expenses and bank-account records
- Persistent sponsor/funding/proposal pipeline
- NPO governance and compliance resources
- Products, customers, orders and camps
- AI-layer storage for conversations, reports, proposals and recommendations
- Offline deterministic `/chat` decision support
- WhatsApp queue ready for a future Meta/Twilio delivery adapter
- Dashboard, Swagger/ReDoc, migrations, seed data, tests and CI

## Design principles

1. **One database authority.** All models use `ai_agent.modules.database.Base` and `SessionLocal`.
2. **Preserve existing data.** Local SQLite upgrades are additive; no tables are dropped by startup migration.
3. **Typed core workflows.** Frequent academy operations use `/crm` Pydantic routes.
4. **Complete extensibility.** The full mapped schema is available through `/faos` administration routes.
5. **No fake integrations.** WhatsApp delivery and generative-AI providers remain optional until real credentials/providers are configured.
6. **Human accountability.** Legal, financial, governance and externally sent/generated material requires appropriate review.

## Start point

From the repository root on Windows CMD:

```cmd
python scripts\migrate_db.py
python scripts\seed_ryt.py
start.bat
```

Then open `/dashboard/` or `/docs` on the local server. See the root `README.md` for complete installation, configuration, testing and production guidance.
