-- Clean slate (safe on a new project)
drop table if exists public.tasks cascade;
drop table if exists public.users cascade;
drop table if exists public.companies cascade;
drop function if exists public.current_company_id() cascade;
drop function if exists public.current_user_role() cascade;
drop function if exists public.set_updated_at() cascade;
drop type if exists public.task_status cascade;
drop type if exists public.user_role cascade;

create extension if not exists pgcrypto;

create type public.user_role as enum ('manager', 'employee');
create type public.task_status as enum ('pending', 'in_progress', 'completed');

create table public.companies (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  created_at timestamptz not null default now()
);

create table public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  company_id uuid not null references public.companies(id) on delete restrict,
  full_name text not null,
  email text not null unique,
  role public.user_role not null default 'employee',
  created_at timestamptz not null default now(),
  constraint users_id_company_unique unique (id, company_id)
);

create table public.tasks (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  title text not null check (char_length(title) between 1 and 200),
  description text check (char_length(description) <= 2000),
  status public.task_status not null default 'pending',
  assigned_to uuid not null,
  created_by uuid not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint tasks_assignee_same_company
    foreign key (assigned_to, company_id) references public.users (id, company_id),
  constraint tasks_creator_same_company
    foreign key (created_by, company_id) references public.users (id, company_id)
);

create index tasks_company_status_idx on public.tasks (company_id, status);
create index tasks_assigned_to_idx on public.tasks (assigned_to);
create index users_company_idx on public.users (company_id);

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end; $$;

create trigger tasks_set_updated_at
before update on public.tasks
for each row execute function public.set_updated_at();

create or replace function public.current_company_id()
returns uuid language sql stable security definer set search_path = public as $$
  select company_id from public.users where id = auth.uid()
$$;

create or replace function public.current_user_role()
returns public.user_role language sql stable security definer set search_path = public as $$
  select role from public.users where id = auth.uid()
$$;

alter table public.companies enable row level security;
alter table public.users     enable row level security;
alter table public.tasks     enable row level security;

create policy "read own company" on public.companies
  for select to authenticated using (id = public.current_company_id());

create policy "read company members" on public.users
  for select to authenticated using (company_id = public.current_company_id());

create policy "managers read company tasks, employees read assigned" on public.tasks
  for select to authenticated
  using (
    company_id = public.current_company_id()
    and (public.current_user_role() = 'manager' or assigned_to = auth.uid())
  );

create policy "managers create tasks in own company" on public.tasks
  for insert to authenticated
  with check (
    company_id = public.current_company_id()
    and public.current_user_role() = 'manager'
    and created_by = auth.uid()
  );

create policy "update tasks in own company" on public.tasks
  for update to authenticated
  using (
    company_id = public.current_company_id()
    and (public.current_user_role() = 'manager' or assigned_to = auth.uid())
  )
  with check (company_id = public.current_company_id());

revoke all on public.companies, public.users, public.tasks from anon;
revoke update on public.tasks from authenticated;
grant update (status) on public.tasks to authenticated;


-- Confirm the tables exist
select table_name from information_schema.tables
where table_schema = 'public' order by table_name;


-- to verify
select email, role, company_id from public.users;