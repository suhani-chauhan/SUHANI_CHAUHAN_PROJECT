# Multi-Tenant Task Management

FastAPI + Supabase (PostgreSQL, Auth, RLS) backend and a React + TypeScript frontend.
Managers assign tasks to employees in their company; employees update status on their own tasks.

## Architecture
- `supabase/` – schema, RLS policies, seed data, example queries
- `backend/app/routers` – HTTP layer only (status codes, request/response models)
- `backend/app/services` – business logic and data access
- `backend/app/schemas` – Pydantic validation models
- `backend/app/core` – config, auth dependency, domain exceptions
- `frontend/src` – `api/` (typed client), `utils/` (filter + completion %), `components/`, `types/`

## Setup
1. **Supabase:** create a project. Disable email confirmation (Auth → Providers → Email). Run `supabase/schema.sql`. Create 4 users in Auth (alice/bob for Acme, gina/hank for Globex), then fill their UUIDs into `supabase/seed.sql` and run it.
2. **Backend:**
```bash
   cd backend && python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env   # fill SUPABASE_URL and SUPABASE_ANON_KEY
   uvicorn app.main:app --reload
```
   API docs: http://localhost:8000/docs
3. **Frontend:**
```bash
   cd frontend && npm install
   cp .env.example .env   # fill the three variables
   npm run dev
```
4. **Tests:** `cd backend && pytest -q` and `cd frontend && npm test`

## API
| Method | Path | Description | Success |
|---|---|---|---|
| POST | /tasks | Manager creates a task for an employee in their company | 201 |
| GET | /tasks?status= | List tasks visible to the caller | 200 |
| PATCH | /tasks/{id} | Update task status | 200 |

Errors: 401 (no/invalid token), 403 (employee creating a task), 404 (task not found or not visible), 422 (validation).

## Security: how cross-company access is prevented
1. **Identity comes from a verified JWT.** The backend validates the Supabase token on every request. User id and company are never taken from request parameters.
2. **Tenant is derived server-side.** `company_id` is read from the caller's profile. Request bodies reject unknown fields (`extra="forbid"`), so sending a `company_id` returns 422.
3. **RLS enforces isolation in the database.** The backend queries Postgres *as the user* (anon key + user JWT, no service key), so every query is filtered by `company_id = current_company_id()`. Even a bug in the API code cannot return another company's rows.
4. **Manipulated IDs are harmless.** A task id from another company is invisible under RLS, so PATCH returns 404 (same as a nonexistent id, so existence is not leaked).
5. **DB constraints back it up.** Composite foreign keys `(assigned_to, company_id)` and `(created_by, company_id)` make it impossible to assign a task to a user from another company. Clients can only update the `status` column (column-level grant), there is no DELETE policy, and users cannot modify roles or companies.

## Assumptions
- A user belongs to exactly one company; role is `manager` or `employee`.
- Employees see only tasks assigned to them; managers see all tasks in their company.
- Any status transition is allowed.
- Users are created through Supabase Auth, and profiles are seeded manually.