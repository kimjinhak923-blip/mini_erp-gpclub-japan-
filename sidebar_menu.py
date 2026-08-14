import datetime
import pytz
import streamlit as st

def render_sidebar():
    """공통 사이드바 Rendering"""
    if not st.session_state.get("logged_in_user"):
        st.warning("🔒 로그인이 필요합니다.")
        if st.button("🔑 로그인 화면으로 이동", type="primary", use_container_width=True):
            st.switch_page("01_ERP_Main.py")
        st.stop()

    user = st.session_state.logged_in_user

    # 3. 메뉴 하단 번역 선택기 복구
    st.sidebar.subheader("🌐 번역 선택 / Language")
    current_lang = st.session_state.get("lang", "한국어")
    selected_lang = st.sidebar.selectbox(
        "언어 선택",
        ["한국어", "日本語", "English"],
        index=["한국어", "日本語", "English"].index(current_lang) if current_lang in ["한국어", "日本語", "English"] else 0,
        label_visibility="collapsed"
    )
    if selected_lang != current_lang:
        st.session_state.lang = selected_lang
        st.rerun()

    st.sidebar.markdown("---")

    # 4. 사용자 정보 및 로그아웃
    st.sidebar.markdown(f"👤 **접속자**: {user['name']} ({user.get('position', '사원')})")
    
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    current_tokyo_time = datetime.datetime.now(tokyo_tz).strftime("%Y-%m-%d %H:%M:%S")
    st.sidebar.caption(f"🕒 도쿄 시간: {current_tokyo_time}")

    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.switch_page("01_ERP_Main.py")
