import streamlit as st
import secrets  # secrets 모듈 명시적 import
from utils.db_client import supabase

def login(email, password):
    try:
        # Supabase Auth 로그인 처리
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            st.session_state["user"] = res.user
            st.session_state["access_token"] = res.session.access_token
            return True, "로그인 성공"
        return False, "아이디 또는 비밀번호가 올바르지 않습니다."
    except Exception as e:
        return False, f"로그인 처리 중 DB 오류가 발생했습니다: {str(e)}"

def require_auth():
    if "user" not in st.session_state or not st.session_state["user"]:
        st.warning("로그인이 필요한 페이지입니다.")
        st.stop()
