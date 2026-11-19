# Multi-Tenant Task Management

A task management system for a multi-company environment. Managers assign tasks to employees in their own company; employees update the status of tasks assigned to them. Built with FastAPI, Supabase (PostgreSQL, Auth, Row Level Security) and React + TypeScript.

## Architecture

```
supabase/   schema.sql (tables, RLS, grants), seed.sql, queries.sql
backend/    FastAPI app
  app/routers/    HTTP layer only (status codes, request/response models)
  app/services/   business logic and data access
  app/schemas/    Pydantic validation models
  app/core/       config, auth dependency, domain exceptions
  app/db/         Supabase client factories
  tests/          pytest endpoint tests
frontend/   React + TypeScript (Vite)
  src/types/      Task types and runtime type guards
  src/utils/      filterTasksByStatus, calculateCompletionPercentage (+ tests)
  src/api/        typed fetch client with error handling
  src/components/ LoginForm, TaskForm, TaskList
```

Request flow: React -> FastAPI (verifies the Supabase JWT) -> service layer -> Postgres queried **as the logged-in user**, so Row Level Security applies to every query.

## Setup

### 1. Supabase
1. Create a Supabase project. In Authentication > Providers > Email, turn off "Confirm email".
2. In the SQL Editor, run `supabase/schema.sql`.
3. In Authentication > Users, create four users with auto-confirm: `alice@acme.test`, `bob@acme.test`, `gina@globex.test`, `hank@globex.test` (demo password: `Test@12345`).
4. Run `supabase/seed.sql`. It creates two companies and links the users by email.

### 2. Backend
Windows (PowerShell):
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then fill SUPABASE_URL and SUPABASE_ANON_KEY
uvicorn app.main:app --reload
```
macOS / Linux:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
copy .env.example .env      # (cp on macOS/Linux) fill the three VITE_ variables
npm run dev
```
App: http://localhost:5173

### 4. Tests
```bash
cd backend && python -m pytest -q
cd frontend && npm test
```

## Demo accounts

| User | Company | Role |
|---|---|---|
| alice@acme.test | Acme Corp | manager |
| bob@acme.test | Acme Corp | employee |
| gina@globex.test | Globex Inc | manager |
| hank@globex.test | Globex Inc | employee |

Password for all demo accounts: `Test@12345`

## API

| Method | Path | Description | Success |
|---|---|---|---|
| POST | /tasks | Manager creates a task for an employee in their company | 201 |
| GET | /tasks?status= | List tasks visible to the caller, optional status filter | 200 |
| PATCH | /tasks/{id} | Update task status | 200 |

Errors: 401 (missing or invalid token), 403 (employee creating a task), 404 (task not found or not visible), 422 (validation failure).

## Security: how cross-company access is prevented

1. **Identity comes from a verified JWT.** The backend validates the Supabase token on every request. The user is never identified by a request parameter.
2. **The tenant is derived server-side.** `company_id` is read from the caller's profile. Request bodies reject unknown fields (`extra="forbid"`), so a client that sends its own `company_id` gets a 422.
3. **Row Level Security enforces isolation in the database.** The backend queries Postgres with the anon key plus the user's JWT (no service key anywhere), so every query is filtered by `company_id = current_company_id()`. Even a bug in the API code cannot return another company's rows.
4. **Manipulated IDs are harmless.** A task id from another company is invisible under RLS, so PATCH returns 404, the same as for a nonexistent id. Existence is not leaked.
5. **Database constraints back it up.** Composite foreign keys `(assigned_to, company_id)` and `(created_by, company_id)` make it impossible to assign a task to a user from another company. Clients can only update the `status` column (column-level grant). There is no DELETE policy, and users cannot change roles or companies.

## Assumptions

- A user belongs to exactly one company, with the role `manager` or `employee`.
- Employees see only tasks assigned to them; managers see all tasks in their company.
- Any status transition is allowed (`pending`, `in_progress`, `completed`).
- Users are created through Supabase Auth and their profiles are seeded by SQL.
- Task titles and descriptions cannot be edited after creation (only status).
