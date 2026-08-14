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

    # 1. 상단 클릭 불가능한 ERP Main 텍스트
    st.sidebar.markdown("### 🏢 **ERP Main**")
    st.sidebar.caption("사내 통합 관리 시스템")
    st.sidebar.markdown("---")

    # 2. 요청 순서 1~10번 메뉴
    st.sidebar.subheader("📌 메뉴")
    st.sidebar.page_link("pages/01_⏱️_출퇴근시스템.py", label="1. 출퇴근시스템")
    st.sidebar.page_link("pages/02_📊_대시보드.py", label="2. 대시보드")
    st.sidebar.page_link("pages/03_💰_매출관리.py", label="3. 매출관리")
    st.sidebar.page_link("pages/04_📜_입출고_이력_조회.py", label="4. 입출고 이력 조회")
    st.sidebar.page_link("pages/05_🔄_재고관리(입출고).py", label="5. 재고관리(입출고)")
    st.sidebar.page_link("pages/06_🤝_거래처_관리.py", label="6. 거래처관리")
    st.sidebar.page_link("pages/07_📦_마스터상품_관리.py", label="7. 마스터상품관리")
    st.sidebar.page_link("pages/08_📅_타임카드_캘린더.py", label="8. 타임카드 캘린더")
    st.sidebar.page_link("pages/09_⚙️_시스템관리.py", label="9. 시스템관리")
    st.sidebar.page_link("pages/10_🕵️_마이페이지.py", label="10. 마이페이지")

    st.sidebar.markdown("---")

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
