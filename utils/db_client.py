import os
import streamlit as st
from supabase import create_client, Client

# 로컬 환경인 경우 .env 파일 로드 시도
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Streamlit Secrets 또는 시스템 환경변수에서 Supabase 정보 추출
SUPABASE_URL = st.secrets.get("SUPABASE_URL") if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") if "SUPABASE_KEY" in st.secrets else os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Supabase 접속 정보(URL, Key)가 설정되지 않았습니다. Secrets 설정을 확인해 주세요.")
    st.stop()

# Supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
