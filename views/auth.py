import streamlit as st
import hashlib
from utils.supabase_client import supabase

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def set_login_session(user):
    st.session_state["user"] = user
    # 브라우저 새로고침 시에도 유지되도록 URL 파라미터에 세션 토큰 저장
    st.query_params["session_token"] = user["id"]

def clear_login_session():
    if "user" in st.session_state:
        del st.session_state["user"]
    st.query_params.clear()

def check_auto_login():
    """새로고침 시 자동 로그인 세션 복구"""
    if "user" not in st.session_state and "session_token" in st.query_params:
        user_id = st.query_params["session_token"]
        try:
            res = supabase.table("user_profiles").select("*").eq("id", user_id).eq("status", "APPROVED").execute()
            if res.data:
                st.session_state["user"] = res.data[0]
        except Exception:
            st.query_params.clear()

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
                    set_login_session(user)
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
        
        # 권한 선택 옵션
        role_display = st.selectbox(
            "희망 권한 선택",
            ["방문자 (조회만 가능)", "사원 (등록/수정 가능)", "관리자 (전체 관리)"]
        )
        
        role_map = {
            "방문자 (조회만 가능)": "GUEST",
            "사원 (등록/수정 가능)": "STAFF",
            "관리자 (전체 관리)": "ADMIN"
        }
        
        submitted = st.form_submit_button("가입 신청")
        
        if submitted and username and password and full_name:
            hashed_pw = hash_password(password)
            selected_role = role_map[role_display]
            try:
                supabase.table("user_profiles").insert({
                    "username": username,
                    "password_hash": hashed_pw,
                    "full_name": full_name,
                    "role": selected_role,
                    "status": "PENDING"
                }).execute()
                st.success(f"가입 신청이 완료되었습니다. (신청 권한: {selected_role}) 관리자 승인 후 이용 가능합니다.")
            except Exception as e:
                st.error(f"가입 신청 실패 (아이디 중복 확인): {e}")
