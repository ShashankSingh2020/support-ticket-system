# Enterprise Intelligent Support Ticket System

Production-ready backend support ticket management system built on a modular Django monolith architecture with asynchronous AI classification, configurable SLA monitoring, and role-based access control.

---

## 1. Architecture Overview
- **Application Core**: Django 5 + Django REST Framework.
- **Identity & Access Control**: Custom email-based User model with 4 distinct roles (`ADMIN`, `MANAGER`, `AGENT`, `CUSTOMER`) enforced via server-side DRF permissions.
- **Workflow & Audit**: State-machine status transitions and immutable audit logs (`TicketEvent`) captured on every action.
- **Asynchronous Task Queue**: Celery backed by Redis, using `transaction.on_commit` hooks to prevent race conditions during task dispatch.
- **AI Classification**: Dual-mode engine featuring a deterministic local mock mode (no keys required) and production Google Gemini integration.
- **Documentation & Throttling**: Interactive OpenAPI 3.0 Swagger docs (`drf-spectacular`) and rate-limited endpoints.

---

## 2. Local Setup (PowerShell)

### Virtual Environment Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt