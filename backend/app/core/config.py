import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def _env(name: str, *fallbacks: str) -> str:
	for key in (name, *fallbacks):
		if val := os.environ.get(key):
			return val
	return ""


# Prefer service role key for backend writes; fall back to anon if explicitly desired
url: str = _env("SUPABASE_URL", "REACT_APP_SUPABASE_URL")
key: str = _env("SUPABASE_SERVICE_ROLE_KEY", "REACT_APP_SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY", "REACT_APP_SUPABASE_ANON_KEY")

if not url or not key:
	raise RuntimeError("Supabase URL/KEY missing. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (preferred) or the REACT_APP_* equivalents.")

supabase: Client = create_client(url, key)
