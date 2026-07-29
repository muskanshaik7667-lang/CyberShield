import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(url, key)

try:
    # Use admin API to create user, which bypasses email confirmation
    user = supabase.auth.admin.create_user({
        "email": "test@example.com",
        "password": "password123",
        "email_confirm": True
    })
    print("Test user created successfully.")
except Exception as e:
    print(f"Error creating user (might already exist): {e}")
