insert into public.companies (id, name) values
  ('11111111-1111-1111-1111-111111111111', 'Acme Corp'),
  ('22222222-2222-2222-2222-222222222222', 'Globex Inc')
on conflict (id) do nothing;

insert into public.users (id, company_id, full_name, email, role)
select au.id, v.company_id::uuid, v.full_name, au.email, v.role::public.user_role
from (values
  ('alice@acme.test',  '11111111-1111-1111-1111-111111111111', 'Alice Manager', 'manager'),
  ('bob@acme.test',    '11111111-1111-1111-1111-111111111111', 'Bob Employee',  'employee'),
  ('gina@globex.test', '22222222-2222-2222-2222-222222222222', 'Gina Manager',  'manager'),
  ('hank@globex.test', '22222222-2222-2222-2222-222222222222', 'Hank Employee', 'employee')
) as v(email, company_id, full_name, role)
join auth.users au on au.email = v.email;