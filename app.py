import streamlit as st
import hashlib
from supabase import create_client, Client

# Supabase 연결 설정
SUPABASE_URL = st.secrets["SUPABASE_URL"]  # 또는 "https://your-project.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]  # 또는 "your-anon-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 비밀번호 SHA-256 해시 함수
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# 로그인 검증 함수
def login(username, password):
    hashed_pw = hash_password(password)
    
    # DB 조회
    response = supabase.table("user_profiles") \
        .select("*") \
        .eq("username", username) \
        .eq("password_hash", hashed_pw) \
        .eq("status", "APPROVED") \
        .eq("is_active", True) \
        .execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]  # 로그인 성공 시 사용자 정보 반환
    return None

# Streamlit UI
st.title("시스템 로그인")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    input_username = st.text_input("아이디", value="admin")
    input_password = st.text_input("비밀번호", type="password", value="admin123!")
    
    if st.button("로그인"):
        user_info = login(input_username, input_password)
        if user_info:
            st.session_state.user = user_info
            st.success(f"{user_info['full_name']}님 환영합니다!")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않거나 승인되지 않은 계정입니다.")
else:
    st.write(f"현재 로그인 계정: **{st.session_state.user['username']}** ({st.session_state.user['role']})")
    if st.button("로그아웃"):
        st.session_state.user = None
        st.rerun()
