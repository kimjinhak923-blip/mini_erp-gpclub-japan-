import streamlit as st
from utils.i18n import LANG_MAP_TO_CODE, LANG_MAP_TO_NAME, get_language, txt


def render_sidebar():
    with st.sidebar:
        current_code = get_language()
        current_name = LANG_MAP_TO_NAME.get(current_code, "한국어")

        options = ["한국어", "日本語", "English"]
        try:
            default_index = options.index(current_name)
        except ValueError:
            default_index = 0

        selected_lang_name = st.selectbox(
            txt("select_language", "🌐 언어 선택 (Language)"),
            options=options,
            index=default_index,
            key="sidebar_global_language_selectbox",
        )

        selected_code = LANG_MAP_TO_CODE.get(selected_lang_name, "KO")

        if selected_code != current_code:
            st.session_state["lang"] = selected_code
            st.session_state["language"] = selected_code

            if "logged_in_user" in st.session_state and isinstance(
                st.session_state["logged_in_user"], dict
            ):
                st.session_state["logged_in_user"]["language"] = selected_code

            st.rerun()

        st.markdown("---")

        user = st.session_state.get("logged_in_user")
        if user and isinstance(user, dict):
            st.markdown(
                f"👤 **{user.get('name', '')}** ({user.get('position', txt('default_position', '사원'))})"
            )
            st.caption(
                f"🔑 {txt('label_role', '권한')}: {user.get('role', txt('default_role', '일반 사용자'))}"
            )
            st.markdown("---")

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

        if user and st.button(
            txt("btn_logout", "🚪 로그아웃"), use_container_width=True
        ):
            st.session_state["logged_in_user"] = None
            st.rerun()
