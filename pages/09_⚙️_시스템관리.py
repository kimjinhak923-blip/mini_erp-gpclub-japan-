import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# -----------------------------------------------------------------------------
# 1. 다국어 사전 정의 (한국어 / 日本語 / English)
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "KO": {
        "page_title": "시스템관리",
        "title": "⚙️ 시스템 및 사용자 관리",
        "access_error": "관리자(CEO)만 접근할 수 있는 메뉴입니다.",
        "tab1": "👤 사용자 승인 및 권한 관리",
        "tab2": "🏢 공통 코드 관리",
        # Tab 1: Users
        "sub_users": "전체 사용자 목록",
        "btn_save_users": "💾 사용자 설정 저장",
        "msg_users_saved": "사용자 정보가 변경되었습니다.",
        # Tab 2: Common Codes
        "sub_codes": "창고 / 직급 목록 관리",
        "header_wh": "📋 현재 창고 목록",
        "label_new_wh": "새 창고 추가",
        "btn_add_wh": "창고 추가",
        "msg_wh_added": "창고가 추가되었습니다.",
        "header_pos": "📋 현재 직급 목록",
        "label_new_pos": "새 직급 추가",
        "btn_add_pos": "직급 추가",
        "msg_pos_added": "직급이 추가되었습니다.",
    },
    "JA": {
        "page_title": "システム管理",
        "title": "⚙️ システムおよびユーザー管理",
        "access_error": "管理者(CEO)のみアクセスできるメニューです。",
        "tab1": "👤 ユーザー承認および権限管理",
        "tab2": "🏢 共通コード管理",
        "sub_users": "全ユーザー一覧",
        "btn_save_users": "💾 ユーザー設定を保存",
        "msg_users_saved": "ユーザー情報が変更されました。",
        "sub_codes": "倉庫 / 役職一覧管理",
        "header_wh": "📋 現在の倉庫一覧",
        "label_new_wh": "新規倉庫追加",
        "btn_add_wh": "倉庫を追加",
        "msg_wh_added": "倉庫が追加されました。",
        "header_pos": "📋 現在の役職一覧",
        "label_new_pos": "新規役職追加",
        "btn_add_pos": "役職を追加",
        "msg_pos_added": "役職が追加されました。",
    },
    "EN": {
        "page_title": "System Management",
        "title": "⚙️ System & User Management",
        "access_error": "This menu is restricted to Administrators (CEO) only.",
        "tab1": "👤 User Approval & Permissions",
        "tab2": "🏢 Common Code Management",
        "sub_users": "All Users List",
        "btn_save_users": "💾 Save User Settings",
        "msg_users_saved": "User information updated successfully.",
        "sub_codes": "Warehouse / Position List Management",
        "header_wh": "📋 Current Warehouse List",
        "label_new_wh": "Add New Warehouse",
        "btn_add_wh": "Add Warehouse",
        "msg_wh_added": "Warehouse added successfully.",
        "header_pos": "📋 Current Position List",
        "label_new_pos": "Add New Position",
        "btn_add_pos": "Add Position",
        "msg_pos_added": "Position added successfully.",
    },
}

# -----------------------------------------------------------------------------
# 2. 세션 언어 상태 감지 및 설정 ('lang' / 'language' 모두 호환)
# -----------------------------------------------------------------------------
raw_lang = st.session_state.get("lang") or st.session_state.get("language") or "KO"
lang_mapping = {
    "한국어": "KO",
    "KO": "KO",
    "日本語": "JA",
    "JA": "JA",
    "English": "EN",
    "EN": "EN",
}
current_lang = lang_mapping.get(raw_lang, "KO")
t = TRANSLATIONS[current_lang]

# -----------------------------------------------------------------------------
# 3. Streamlit Page Config 설정 (최상단 고정)
# -----------------------------------------------------------------------------
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 렌더링
render_sidebar()

# 5. 로그인 사용자 세션 정보 확인
user = st.session_state.get("logged_in_user", {})

# -----------------------------------------------------------------------------
# 6. 메인 UI 렌더링
# -----------------------------------------------------------------------------
st.title(t["title"])
st.markdown("---")

# 권한 체크 ("관리자" 키워드 호환 검사)
if "관리자" not in user.get("role", ""):
    st.error(t["access_error"])
else:
    tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

    # --- [TAB 1] 사용자 승인 및 권한 관리 ---
    with tab1:
        st.subheader(t["sub_users"])
        if st.session_state.get("users"):
            df_users = pd.DataFrame(st.session_state.users)
            edited_users = st.data_editor(
                df_users, num_rows="dynamic", use_container_width=True
            )
            if st.button(t["btn_save_users"]):
                st.session_state.users = edited_users.to_dict("records")
                st.success(t["msg_users_saved"])
                st.rerun()

    # --- [TAB 2] 공통 코드 관리 (창고 / 직급) ---
    with tab2:
        st.subheader(t["sub_codes"])
        col1, col2 = st.columns(2)

        # 창고 관리
        with col1:
            st.write(f"**{t['header_wh']}**")
            st.write(st.session_state.get("warehouses", []))
            new_wh = st.text_input(t["label_new_wh"])
            if st.button(t["btn_add_wh"]):
                if "warehouses" not in st.session_state:
                    st.session_state.warehouses = []
                if new_wh and new_wh not in st.session_state.warehouses:
                    st.session_state.warehouses.append(new_wh)
                    st.success(t["msg_wh_added"])
                    st.rerun()

        # 직급 관리
        with col2:
            st.write(f"**{t['header_pos']}**")
            st.write(st.session_state.get("positions", []))
            new_pos = st.text_input(t["label_new_pos"])
            if st.button(t["btn_add_pos"]):
                if "positions" not in st.session_state:
                    st.session_state.positions = []
                if new_pos and new_pos not in st.session_state.positions:
                    st.session_state.positions.append(new_pos)
                    st.success(t["msg_pos_added"])
                    st.rerun()
