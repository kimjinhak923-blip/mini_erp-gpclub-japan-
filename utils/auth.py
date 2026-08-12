import streamlit as st
import secrets
from utils.db_client import supabase

def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            st.session_state["user"] = res.user
            st.session_state["access_token"] = res.session.access_token
            return True, "로그인 성공!"
        return False, "이메일 또는 비밀번호가 올바르지 않습니다."
    except Exception as e:
        return False, f"로그인 처리 중 오류가 발생했습니다: {str(e)}"

def logout():
    st.session_state["user"] = None
    st.session_state["access_token"] = None
    st.rerun()

def require_auth():
    if "user" not in st.session_state or not st.session_state["user"]:
        st.title("🔐 ERP 시스템 로그인")
        st.caption("시스템 접근을 위해 로그인해 주세요.")
        
        _, col, _ = st.columns([1, 2, 1])
        with col:
            with st.form("auth_login_form"):
                email = st.text_input("이메일 (ID)", placeholder="user@company.com")
                password = st.text_input("비밀번호", type="password")
                submit = st.form_submit_button("🔑 로그인", type="primary", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("이메일과 비밀번호를 모두 입력해 주세요.")
                    else:
                        success, msg = login(email, password)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        st.stop()

    user = st.session_state["user"]
    user_email = getattr(user, "email", "인증된 사용자")
    st.sidebar.markdown("---")
    st.sidebar.caption(f"👤 **{user_email}**")
    if st.sidebar.button("🔓 로그아웃", key="auth_logout_btn", use_container_width=True):
        logout()
