import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


@st.cache_data(ttl=120)
def fetch_crane_records():
    response = supabase.table("crane_records").select("*").execute()
    return response.data
