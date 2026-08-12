import streamlit as st
import secrets
from utils.db_client import supabase
from utils.i18n import t, render_lang_selector

def init_auth():
    """URL Query Parameter를 활용하여 브라우저 재접속 시에도 자동 로그인 상태 유지"""
    if "user" not in st.session_state:
        st.session_state["user"] = None

    # URL 토큰을 통한 자동 로그인 확인
    query_params = st.query_params
    auth_token = query_params.get("session_token")

    if not st.session_state["user"] and auth_token:
        # DB에서 토큰 검증
        res = supabase.table("employees").select("*").eq("session_token", auth_token).eq("is_active", True).execute()
        if res.data:
            st.session_state["user"] = res.data[0]

def render_login_page():
    st.title(f"🔐 {t('login')}")
    render_lang_selector()
    
    with st.form("login_form"):
        email = st.text_input(t("email"), placeholder="user@company.com").strip()
        password = st.text_input(t("password"), type="password")
        remember_me = st.checkbox(t("remember_me"), value=True)
        
        submitted = st.form_submit_button(t("login_btn"))
        
        if submitted:
            if not email:
                st.warning("이메일을 입력해 주세요.")
                return
                
            try:
                # DB 조회
                res = supabase.table("employees").select("*").eq("email", email).eq("is_active", True).execute()
                
                if res.data and len(res.data) > 0:
                    user = res.data[0]
                    token = secrets.token_hex(16)
                    
                    if remember_me:
                        try:
                            supabase.table("employees").update({"session_token": token}).eq("id", user["id"]).execute()
                            st.query_params["session_token"] = token
                        except Exception as token_e:
                            st.warning(f"자동 로그인 토큰 저장 중 경고: {token_e}")
                    
                    st.session_state["user"] = user
                    st.success(t("login_success"))
                    st.rerun()
                else:
                    st.error("등록되지 않은 이메일이거나 비활성화된 계정입니다.")
            except Exception as e:
                st.error(f"로그인 처리 중 DB 오류가 발생했습니다: {e}")

def logout():
    """로그아웃 클릭 시에만 세션 토큰 제거 및 자동 로그인 해제"""
    if st.session_state.get("user"):
        user_id = st.session_state["user"]["id"]
        # DB 토큰 삭제
        supabase.table("employees").update({"session_token": None}).eq("id", user_id).execute()
    
    st.session_state["user"] = None
    if "session_token" in st.query_params:
        del st.query_params["session_token"]
    st.rerun()

def require_auth():
    init_auth()
    if not st.session_state.get("user"):
        render_login_page()
        st.stop()
        
    # 로그인된 경우 사이드바에 사용자 정보, 다국어 선택기 및 로그아웃 버튼 표시
    user = st.session_state["user"]
    st.sidebar.markdown(f"👤 **{user['name']}** ({user.get('department', '일반')})")
    render_lang_selector()
    if st.sidebar.button(f"🚪 {t('logout')}"):
        logout()
