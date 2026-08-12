import datetime
import pytz
import streamlit as st

def render_sidebar():
    """안전한 공통 사이드바 (번역 + 로그인 세션 유지 + 지정된 순서)"""

    # 1. 로그인 상태 체크 (미로그인 시 경고 후 메인 이동 안내)
    if not st.session_state.get("logged_in_user"):
        st.warning("🔒 로그인이 필요합니다. 메인 화면으로 이동합니다.")
        if st.button("🔑 로그인 화면으로 이동", type="primary", use_container_width=True):
            st.switch_page("01_ERP_Main.py")
        st.stop()  # 로그인 안 되었으면 아래 코드 실행 중단

    user = st.session_state.logged_in_user

    # 2. 최상단: 클릭 불가능한 텍스트 표기
    st.sidebar.markdown("### 🏢 **ERP Main**")
    st.sidebar.caption("사내 통합 관리 시스템")
    st.sidebar.markdown("---")

    # 3. 요청하신 1~10번 메뉴 순서
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

    # 4. 메뉴 바로 아래: 번역(언어) 선택기 복구
    st.sidebar.subheader("🌐 번역 선택 / Language")
    current_lang = st.session_state.get("lang", "한국어")
    
    selected_lang = st.sidebar.selectbox(
        "언어 선택",
        ["한국어", "日本語", "English"],
        index=["한국어", "日本語", "English"].index(current_lang) if current_lang in ["한국어", "日本語", "English"] else 0,
        label_visibility="collapsed"
    )
    
    # 언어 변경 시 세션 업데이트 및 리로드
    if selected_lang != st.session_state.get("lang"):
        st.session_state.lang = selected_lang
        st.rerun()

    st.sidebar.markdown("---")

    # 5. 접속자 정보 & 도쿄 시간 & 로그아웃
    st.sidebar.markdown(f"👤 **접속자**: {user['name']} ({user.get('position', '사원')})")
    
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    current_tokyo_time = datetime.datetime.now(tokyo_tz).strftime("%Y-%m-%d %H:%M:%S")
    st.sidebar.caption(f"🕒 도쿄 시간: {current_tokyo_time}")

    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.switch_page("01_ERP_Main.py")
