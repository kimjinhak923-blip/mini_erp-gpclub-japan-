import pandas as pd
import streamlit as st

user = st.session_state.get("logged_in_user")
if not user:
    st.warning("로그인이 필요한 페이지입니다. 메인 페이지에서 먼저 로그인해 주세요.")
    st.stop()

st.title("⚙️ 시스템 및 사용자 관리")
st.markdown("---")

if "관리자" not in user["role"]:
    st.error("관리자(CEO)만 접근할 수 있는 메뉴입니다.")
    st.stop()

tab1, tab2 = st.tabs(["👤 사용자 승인 및 권한 관리", "🏢 공통 코드 관리"])

with tab1:
    st.subheader("전체 사용자 목록")
    if st.session_state.users:
        df_users = pd.DataFrame(st.session_state.users)
        edited_users = st.data_editor(
            df_users, num_rows="dynamic", use_container_width=True
        )
        if st.button("💾 사용자 설정 저장"):
            st.session_state.users = edited_users.to_dict("records")
            st.success("사용자 정보가 변경되었습니다.")
            st.rerun()

with tab2:
    st.subheader("창고 / 직급 목록 관리")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📋 **현재 창고 목록**")
        st.write(st.session_state.warehouses)
        new_wh = st.text_input("새 창고 추가")
        if st.button("창고 추가"):
            if new_wh and new_wh not in st.session_state.warehouses:
                st.session_state.warehouses.append(new_wh)
                st.success("창고가 추가되었습니다.")
                st.rerun()

    with col2:
        st.write("📋 **현재 직급 목록**")
        st.write(st.session_state.positions)
        new_pos = st.text_input("새 직급 추가")
        if st.button("직급 추가"):
            if new_pos and new_pos not in st.session_state.positions:
                st.session_state.positions.append(new_pos)
                st.success("직급이 추가되었습니다.")
                st.rerun()
