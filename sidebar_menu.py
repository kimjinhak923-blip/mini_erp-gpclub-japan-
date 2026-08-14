import streamlit as st
from i18n import txt, render_live_clock

def render_sidebar():
    """공통 사이드바 Rendering"""
    if not st.session_state.get("logged_in_user"):
        st.warning(txt("login_required"))
        if st.button(txt("go_to_login"), type="primary", use_container_width=True):
            st.switch_page("01_ERP_Main.py")
        st.stop()

    user = st.session_state.logged_in_user

    # 언어 선택기
    st.sidebar.subheader(txt("lang_select"))
    current_lang = st.session_state.get("lang", user.get("lang", "한국어"))
    selected_lang = st.sidebar.selectbox(
        "언어 선택",
        ["한국어", "日本語", "English"],
        index=["한국어", "日本語", "English"].index(current_lang) if current_lang in ["한국어", "日本語", "English"] else 0,
        label_visibility="collapsed"
    )
    if selected_lang != current_lang:
        st.session_state.lang = selected_lang
        # 유저 선호 언어도 세션 내 동기화
        if st.session_state.logged_in_user:
            st.session_state.logged_in_user["lang"] = selected_lang
        st.rerun()

    st.sidebar.markdown("---")

    # 사용자 정보 및 로그아웃
    st.sidebar.markdown(f"{txt('logged_in_as')}: **{user['name']}** ({user.get('position', '사원')})")
    
    st.sidebar.markdown(f"**{txt('live_clock')}**")
    render_live_clock()

    if st.sidebar.button(txt("logout"), use_container_width=True):
        st.session_state.logged_in_user = None
        st.switch_page("01_ERP_Main.py")
