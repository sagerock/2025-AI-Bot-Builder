-- Cairn session tracking
-- Applied to mail tool Supabase project (ref: ckloewflialohuvixmvd)
-- Date: 2026-05-28

create table if not exists cairn_sessions (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  contact_id uuid references contacts(id),
  topic text,
  outcome text,
  transcript jsonb,
  booked_at timestamptz,
  created_at timestamptz default now()
);

create index if not exists cairn_sessions_contact_id_idx on cairn_sessions(contact_id);
create index if not exists cairn_sessions_outcome_idx on cairn_sessions(outcome);
create index if not exists cairn_sessions_session_id_idx on cairn_sessions(session_id);
