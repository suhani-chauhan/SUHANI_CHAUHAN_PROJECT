from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache
def get_anon_client() -> Client:
    """Shared client, used only to verify tokens."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_user_client(token: str) -> Client:
    """Per-request client acting AS the user, so Postgres RLS applies."""
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.postgrest.auth(token)
    return client