from db import supabase

try:
    scans = supabase.table("scans").select("*", count="exact").execute()
    print(f"Scans row count: {scans.count}")
except Exception as e:
    print(f"Scans error: {e}")

try:
    results = supabase.table("results").select("*", count="exact").execute()
    print(f"Results row count: {results.count}")
except Exception as e:
    print(f"Results error: {e}")
