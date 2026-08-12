import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

load_dotenv()

@st.cache_resource
def init_supabase() -> Client:
    # Streamlit Secrets 또는 .env 환경변수 읽기
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")
    
    if not url or not key:
        st.error("⚠️ Supabase URL 및 Key가 설정되지 않았습니다. .env 또는 .streamlit/secrets.toml 설정을 확인해주세요.")
        st.stop()
        
    return create_client(url, key)

supabase = init_supabase()
