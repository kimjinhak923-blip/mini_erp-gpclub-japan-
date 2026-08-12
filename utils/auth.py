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
    # 1. 로그인 상태가 아닐 경우 로그인 폼 출력
    if "user" not in st.session_state or not st.session_state["user"]:
        st.title("🔐 ERP 시스템 로그인")
        st.caption("시스템에 접근하려면 인증이 필요합니다.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("global_login_form"):
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
                            st.rerun()  # 로그인 성공 시 화면을 새로고침하여 페이지 내용 로드
                        else:
                            st.error(msg)
        
        # 로그인 폼을 띄운 후 하단 본문 생성을 중단
        st.stop()

    # 2. 로그인된 상태일 경우 사이드바 하단에 사용자 정보 및 로그아웃 버튼 표시
    user = st.session_state["user"]
    user_email = getattr(user, "email", "인증된 사용자")
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"👤 **{user_email}** 님")
    if st.sidebar.button("🔓 로그아웃", key="global_logout_btn", use_container_width=True):
        logout()
