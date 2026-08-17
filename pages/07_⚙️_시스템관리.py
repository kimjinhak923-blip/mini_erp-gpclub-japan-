import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar
from utils.i18n import txt

st.set_page_config(page_title="시스템관리", layout="wide")
render_sidebar()

user = st.session_state.get("logged_in_user")

# DB 테이블 초기화
db.init_db()

st.title("⚙️ 시스템 및 사용자 관리")
st.markdown("---")

if not user or "관리자" not in user.get("role", ""):
    st.error("관리자(CEO)만 접근할 수 있는 메뉴입니다.")
else:
    # 탭 구성: 1. 사용자 관리 / 2. 공통 코드 관리 (연차 승인 탭 제거됨)
    tab1, tab2 = st.tabs(["👤 사용자 승인 및 권한 관리", "🏢 공통 코드 관리"])

    # -------------------------------------------------------------------------
    # TAB 1: 사용자 승인 및 권한 관리 (연차 데이터 제거)
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("전체 사용자 목록")
        if "users" in st.session_state and st.session_state.users:
            df_users = pd.DataFrame(st.session_state.users)

            # 기존 연차 관련 컬럼이 있다면 표에서 표시되지 않도록 제거
            for leave_col in [
                "remaining_leave",
                "granted_leave",
                "annual_leave",
            ]:
                if leave_col in df_users.columns:
                    df_users = df_users.drop(columns=[leave_col])

            edited_users = st.data_editor(
                df_users,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "id": st.column_config.TextColumn("아이디", disabled=True),
                    "name": st.column_config.TextColumn("이름"),
                    "role": st.column_config.TextColumn("권한"),
                    "department": st.column_config.TextColumn("부서"),
                    "position": st.column_config.TextColumn("직급"),
                },
            )

            if st.button("💾 사용자 설정 저장", type="primary"):
                updated_list = edited_users.to_dict("records")
                st.session_state.users = updated_list

                # 현재 로그인 유저 세션 동기화
                for u in updated_list:
                    if u.get("id") == user.get("id"):
                        st.session_state.logged_in_user = u
                        break

                st.success("사용자 정보가 저장되었습니다.")
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: 공통 코드 관리 (창고/직급)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("창고 / 직급 목록 관리")
        col1, col2 = st.columns(2)
        with col1:
            st.write("📋 **현재 창고 목록**")
            st.write(st.session_state.get("warehouses", []))
            new_wh = st.text_input("새 창고 추가")
            if st.button("창고 추가"):
                if "warehouses" not in st.session_state:
                    st.session_state.warehouses = []
                if new_wh and new_wh not in st.session_state.warehouses:
                    st.session_state.warehouses.append(new_wh)
                    st.success("창고가 추가되었습니다.")
                    st.rerun()

        with col2:
            st.write("📋 **현재 직급 목록**")
            st.write(st.session_state.get("positions", []))
            new_pos = st.text_input("새 직급 추가")
            if st.button("직급 추가"):
                if "positions" not in st.session_state:
                    st.session_state.positions = []
                if new_pos and new_pos not in st.session_state.positions:
                    st.session_state.positions.append(new_pos)
                    st.success("직급이 추가되었습니다.")
                    st.rerun()
