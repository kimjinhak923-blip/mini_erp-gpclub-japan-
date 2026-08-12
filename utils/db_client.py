import streamlit as st
from supabase import create_client, Client

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except KeyError as e:
    st.error(f".streamlit/secrets.toml 파일에 {e} 설정이 누락되었습니다.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
