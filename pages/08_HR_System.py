import streamlit as st
import pandas as pd
from datetime import date
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t, render_sidebar

st.set_page_config(page_title=t("nav_hr"), page_icon="⏰", layout="wide")
require_auth()
render_sidebar()

st.title("⏰ 인사 및 근태 관리 시스템")

tab_emp, tab_att = st.tabs(["👤 직원 마스터 관리", "📅 근태 기록 및 조회"])

with tab_emp:
    with st.form("hr_emp_form"):
        st.subheader("새 직원 등록")
        c1, c2, c3, c4 = st.columns(4)
        emp_no = c1.text_input("사번")
        emp_name = c2.text_input("성명")
        dept = c3.text_input("부서")
        pos = c4.text_input("직급")
        j_date = st.date_input("입사일", value=date.today())
        
        if st.form_submit_button("직원 등록") and emp_no and emp_name:
            supabase.table("employees").insert({
                "emp_no": emp_no, "name": emp_name, "department": dept,
                "position": pos, "joined_date": j_date.isoformat()
            }).execute()
            st.success("직원 정보가 등록되었습니다.")
            st.rerun()

    emps = supabase.table("employees").select("*").execute().data or []
    st.dataframe(pd.DataFrame(emps), use_container_width=True)

with tab_att:
    st.subheader("근태 입력 및 현황")
    emps = supabase.table("employees").select("*").execute().data or []
    if emps:
        emp_map = {f"[{e['emp_no']}] {e['name']}": e["id"] for e in emps}
        
        c1, c2, c3 = st.columns(3)
        sel_emp = c1.selectbox("직원 선택", list(emp_map.keys()), key="hr_att_emp")
        att_date = c2.date_input("근무일자", value=date.today(), key="hr_att_date")
        att_status = c3.selectbox("근태 상태", ["정상근무", "지각", "조퇴", "결근", "휴가"], key="hr_att_status")
        
        if st.button("근태 기록 저장"):
            supabase.table("attendance").upsert({
                "employee_id": emp_map[sel_emp],
                "work_date": att_date.isoformat(),
                "status": att_status
            }).execute()
            st.success("근태 기록이 저장되었습니다.")
            
    atts = supabase.table("attendance").select("*, employees(emp_no, name)").execute().data or []
    st.dataframe(pd.DataFrame(atts), use_container_width=True)
