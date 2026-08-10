import streamlit as st
import hashlib
from utils.supabase_client import supabase

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def render_login():
    st.subheader("🔑 로그인")
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")
        
        if submitted:
            hashed_pw = hash_password(password)
            res = supabase.table("user_profiles").select("*").eq("username", username).eq("password_hash", hashed_pw).execute()
            if res.data:
                user = res.data[0]
                if user["status"] == "PENDING":
                    st.warning("⏳ 관리자 승인 대기 중인 계정입니다.")
                elif user["status"] == "REJECTED":
                    st.error("❌ 가입이 거절된 계정입니다.")
                else:
                    st.session_state["user"] = user
                    st.success(f"{user['full_name']}님 환영합니다!")
                    st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

def render_signup():
    st.subheader("📝 회원가입 신청")
    with st.form("signup_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        full_name = st.text_input("이름")
        submitted = st.form_submit_button("가입 신청")
        
        if submitted and username and password and full_name:
            hashed_pw = hash_password(password)
            try:
                supabase.table("user_profiles").insert({
                    "username": username,
                    "password_hash": hashed_pw,
                    "full_name": full_name,
                    "role": "STAFF",
                    "status": "PENDING"
                }).execute()
                st.success("회원가입 신청이 완료되었습니다. 관리자 승인 후 이용 가능합니다.")
            except Exception as e:
                st.error(f"가입 신청 실패 (아이디 중복 확인): {e}")
