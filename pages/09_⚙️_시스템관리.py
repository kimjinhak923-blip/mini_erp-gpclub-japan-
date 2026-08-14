import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar
from utils.i18n import txt

st.set_page_config(page_title="시스템관리", layout="wide")
render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("⚙️ 시스템 및 사용자 관리")
st.markdown("---")

if not user or "관리자" not in user.get("role", ""):
    st.error("관리자(CEO)만 접근할 수 있는 메뉴입니다.")
else:
    tab1, tab2 = st.tabs(["👤 사용자 승인 및 권한 관리", "🏢 공통 코드 관리"])

    with tab1:
        st.subheader("전체 사용자 목록")
        if "users" in st.session_state and st.session_state.users:
            df_users = pd.DataFrame(st.session_state.users)

            # 연차 컬럼(remaining_leave)이 없을 경우 기본값 15.0으로 세팅
            if "remaining_leave" not in df_users.columns:
                df_users["remaining_leave"] = 15.0

            # 표 헤더 한글화 및 입력 방식 설정
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
                    "remaining_leave": st.column_config.NumberColumn(
                        "부여 연차 (일)",
                        help="직원에게 부여된 총 연차 일수입니다.",
                        min_value=0.0,
                        max_value=40.0,
                        step=0.5,
                        format="%.1f 일",
                    ),
                },
            )

            if st.button("💾 사용자 설정 저장", type="primary"):
                updated_list = edited_users.to_dict("records")
                st.session_state.users = updated_list

                # 현재 로그인 유저 정보 동기화
                for u in updated_list:
                    if u.get("id") == user.get("id"):
                        st.session_state.logged_in_user = u
                        break

                st.success(
                    "사용자 정보 및 연차 설정이 성공적으로 저장되었습니다."
                )
                st.rerun()

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
