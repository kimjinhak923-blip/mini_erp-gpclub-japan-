import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="시스템관리", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

user = st.session_state.logged_in_user
is_admin = user.get("role") == "관리자" or user["id"] == "admin"

st.header("⚙️ 시스템 관리 (사용자 및 인사정보 관리)")

t_u1, t_u2 = st.tabs(["👥 전체 계정 수정/관리", "👔 직원 정보 관리"])

with t_u1:
    if is_admin:
        st.subheader("👑 계정 수정 및 승인 관리")
        u_ids = [u["id"] for u in st.session_state.users]
        sel_u = st.selectbox("수정할 계정 선택", u_ids)
        t_user = next(u for u in st.session_state.users if u["id"] == sel_u)

        with st.form("edit_user_form"):
            eu_name = st.text_input("이름", value=t_user["name"])
            eu_pos = st.selectbox("직급", st.session_state.positions)
            eu_dept = st.text_input("부서", value=t_user.get("dept", ""))
            eu_role = st.selectbox("권한", st.session_state.roles)
            eu_status = st.selectbox("상태", ["승인 완료", "승인 대기"])

            if st.form_submit_button("계정 저장"):
                t_user["name"] = eu_name
                t_user["position"] = eu_pos
                t_user["dept"] = eu_dept
                t_user["role"] = eu_role
                t_user["status"] = eu_status
                st.success("수정 저장이 완료되었습니다.")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 등록 계정 현황")
    st.dataframe(pd.DataFrame(st.session_state.users)[
        ["id", "name", "position", "dept", "role", "status", "hire_date", "annual_leave"]
    ], use_container_width=True)

with t_u2:
    st.subheader("👔 직원 인사 정보 관리 (입사일/잔여연차)")
    if is_admin:
        e_ids = [u["id"] for u in st.session_state.users]
        s_e_id = st.selectbox("직원 선택", e_ids)
        t_e = next(u for u in st.session_state.users if u["id"] == s_e_id)

        with st.form("emp_mgmt_form"):
            e_hire = st.date_input("입사일", value=datetime.datetime.strptime(t_e.get("hire_date", str(datetime.date.today())), "%Y-%m-%d").date())
            e_leave = st.number_input("잔여 연차", min_value=0.0, max_value=50.0, value=float(t_e.get("annual_leave", 15.0)), step=0.5)

            if st.form_submit_button("인사정보 저장"):
                t_e["hire_date"] = str(e_hire)
                t_e["annual_leave"] = e_leave
                st.success("저장되었습니다.")
                st.rerun()

    st.markdown("---")
    st.dataframe(pd.DataFrame(st.session_state.users)[
        ["id", "name", "position", "dept", "hire_date", "annual_leave"]
    ], use_container_width=True)
