import streamlit as st
from i18n import render_language_selector, txt


def render_sidebar():
    """공통 사이드바 메뉴 및 언어 선택기 렌더링"""
    with st.sidebar:
        # 1. 🌐 다국어 언어 선택 셀렉트박스 (최상단 배치)
        render_language_selector(container=st.sidebar)
        st.markdown("---")

        # 2. 로그인 사용자 정보 표시
        user = st.session_state.get("logged_in_user")
        if user:
            st.markdown(
                f"👤 **{user.get('name', '')}** ({user.get('position', txt('default_position', '사원'))})"
            )
            st.caption(
                f"🔑 {txt('label_role', '권한')}: {user.get('role', txt('default_role', '일반 사용자'))}"
            )
            st.markdown("---")

        # 3. 메인 메뉴 네비게이션
        st.page_link(
            "pages/01_⏱️_출퇴근시스템.py",
            label=txt("menu_commute", "⏱️ 출퇴근 관리 / 타임카드"),
        )
        st.page_link(
            "pages/02_⚙️_시스템관리.py",
            label=txt("menu_system", "⚙️ 시스템 및 사용자 관리"),
        )
        st.page_link(
            "pages/03_👤_마이페이지.py",
            label=txt("menu_mypage", "👤 마이페이지"),
        )

        st.markdown("---")

        # 4. 로그아웃 버튼
        if user and st.button(
            txt("btn_logout", "🚪 로그아웃"), use_container_width=True
        ):
            st.session_state["logged_in_user"] = None
            st.rerun()
