import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t

st.set_page_config(page_title=t("hr_title"), page_icon="⏰", layout="wide")
require_auth()

user = st.session_state["user"]
user_id = user["id"]
user_name = user["name"]
user_role = user.get("role", "EMPLOYEE")

role_label = t("role_admin") if user_role == "ADMIN" else (t("role_visitor") if user_role == "VISITOR" else t("role_employee"))

st.title(f"⏰ {t('hr_title')} - {user_name} ({role_label})")

# -------------------------------------------------------------------
# [1] 출퇴근 체크 모듈
# -------------------------------------------------------------------
st.subheader(f"📍 {t('today_clock')}")

today = date.today().isoformat()
now_time = datetime.now().strftime("%H:%M:%S")

attendance_res = supabase.table("attendance_logs") \
    .select("*") \
    .eq("employee_id", user_id) \
    .eq("work_date", today) \
    .execute()

today_log = attendance_res.data[0] if attendance_res.data else None

col_in, col_out, col_status = st.columns([1, 1, 2])

with col_in:
    clock_in_time = today_log["clock_in"] if today_log and today_log.get("clock_in") else t("not_checked")
    st.metric(t("clock_in"), clock_in_time)
    
    if user_role == "VISITOR":
        st.button(t("clock_in_btn"), disabled=True, key="in_disabled")
    elif not today_log or not today_log.get("clock_in"):
        if st.button(t("clock_in_btn"), use_container_width=True, type="primary"):
            supabase.table("attendance_logs").insert({
                "employee_id": user_id,
                "work_date": today,
                "clock_in": now_time,
                "status": "PRESENT"
            }).execute()
            st.success(t("clock_in_msg"))
            st.rerun()

with col_out:
    clock_out_time = today_log["clock_out"] if today_log and today_log.get("clock_out") else t("not_checked")
    st.metric(t("clock_out"), clock_out_time)
    
    if user_role == "VISITOR":
        st.button(t("clock_out_btn"), disabled=True, key="out_disabled")
    elif today_log and today_log.get("clock_in") and not today_log.get("clock_out"):
        if st.button(t("clock_out_btn"), use_container_width=True, type="secondary"):
            supabase.table("attendance_logs").update({
                "clock_out": now_time
            }).eq("id", today_log["id"]).execute()
            st.success(t("clock_out_msg"))
            st.rerun()

with col_status:
    status_text = today_log["status"] if today_log else t("not_clocked_in")
    st.info(f"💡 {t('current_status')}: **{status_text}** ({t('today_date')}: {today})")

st.markdown("---")

# -------------------------------------------------------------------
# [2] 연차 현황 및 휴가 신청
# -------------------------------------------------------------------
st.subheader(f"🌴 {t('vacation_info')}")

emp_info_res = supabase.table("employees").select("*").eq("id", user_id).execute()
emp_info = emp_info_res.data[0] if emp_info_res.data else {}

tot_vacation = emp_info.get("total_vacation", 15.0)
used_vacation = emp_info.get("used_vacation", 0.0)
rem_vacation = tot_vacation - used_vacation

v_col1, v_col2, v_col3 = st.columns(3)
v_col1.metric(t("total_vacation"), f"{tot_vacation}")
v_col2.metric(t("used_vacation"), f"{used_vacation}")
v_col3.metric(t("remain_vacation"), f"{rem_vacation}")

with st.expander(t("apply_leave"), expanded=False):
    if user_role == "VISITOR":
        st.warning(t("visitor_leave_warn"))
    else:
        with st.form("leave_request_form"):
            l_col1, l_col2 = st.columns(2)
            s_date = l_col1.date_input(t("start_date"), value=date.today())
            e_date = l_col2.date_input(t("end_date"), value=date.today())
            
            leave_days = (e_date - s_date).days + 1
            reason = st.text_input(t("leave_reason"), placeholder=t("placeholder_reason"))
            
            submit_leave = st.form_submit_button(t("submit_leave_btn"))
            if submit_leave:
                if s_date > e_date:
                    st.error(t("date_range_error"))
                elif leave_days > rem_vacation:
                    st.error(t("leave_exceed_error"))
                else:
                    supabase.table("leave_requests").insert({
                        "employee_id": user_id,
                        "start_date": s_date.isoformat(),
                        "end_date": e_date.isoformat(),
                        "days_count": leave_days,
                        "reason": reason,
                        "status": "PENDING"
                    }).execute()
                    st.success(t("leave_success_msg"))
                    st.rerun()

# -------------------------------------------------------------------
# [3] 관리자 전용: 직원 관리 & 휴가 승인
# -------------------------------------------------------------------
if user_role == "ADMIN":
    st.markdown("---")
    st.subheader(t("admin_hr_menu"))
    
    admin_tab1, admin_tab2 = st.tabs([t("tab_leave_approval"), t("tab_emp_manage")])
    
    with admin_tab1:
        st.markdown(f"##### {t('pending_leave_title')}")
        pending_leaves = supabase.table("leave_requests") \
            .select("*, employees(name, department)") \
            .eq("status", "PENDING") \
            .execute()
        
        if pending_leaves.data:
            for req in pending_leaves.data:
                emp_data = req.get("employees") or {}
                st.write(f"**{emp_data.get('name')}** ({emp_data.get('department')}) | {req['start_date']} ~ {req['end_date']} ({req['days_count']}) | {req['reason']}")
                
                app_col1, app_col2, _ = st.columns([1, 1, 4])
                if app_col1.button(t("btn_approve"), key=f"app_{req['id']}"):
                    supabase.table("leave_requests").update({"status": "APPROVED"}).eq("id", req["id"]).execute()
                    
                    target_emp_id = req["employee_id"]
                    target_emp = supabase.table("employees").select("used_vacation").eq("id", target_emp_id).execute().data[0]
                    new_used = target_emp.get("used_vacation", 0) + req["days_count"]
                    
                    supabase.table("employees").update({"used_vacation": new_used}).eq("id", target_emp_id).execute()
                    st.success(t("leave_approved_msg"))
                    st.rerun()
                    
                if app_col2.button(t("btn_reject"), key=f"rej_{req['id']}"):
                    supabase.table("leave_requests").update({"status": "REJECTED"}).eq("id", req["id"]).execute()
                    st.warning(t("leave_rejected_msg"))
                    st.rerun()
        else:
            st.info(t("no_pending_leave"))

    with admin_tab2:
        st.markdown(f"##### {t('edit_emp_title')}")
        all_emps = supabase.table("employees").select("*").execute()
        
        if all_emps.data:
            df_emps = pd.DataFrame(all_emps.data)
            selected_emp_id = st.selectbox(t("select_emp_label"), df_emps["id"].tolist())
            
            if selected_emp_id:
                target_emp = df_emps[df_emps["id"] == selected_emp_id].iloc[0]
                
                with st.form("edit_employee_form"):
                    e_col1, e_col2, e_col3 = st.columns(3)
                    e_name = e_col1.text_input(t("emp_name"), value=str(target_emp["name"]))
                    e_dept = e_col2.text_input(t("department"), value=str(target_emp.get("department", "")))
                    
                    role_options = ["ADMIN", "EMPLOYEE", "VISITOR"]
                    curr_role_idx = role_options.index(target_emp.get("role", "EMPLOYEE")) if target_emp.get("role") in role_options else 1
                    e_role = e_col3.selectbox(t("role"), role_options, index=curr_role_idx)
                    
                    e_col4, e_col5 = st.columns(2)
                    e_tot_vac = e_col4.number_input(t("alloc_vacation"), value=float(target_emp.get("total_vacation", 15.0)))
                    e_used_vac = e_col5.number_input(t("used_vacation_input"), value=float(target_emp.get("used_vacation", 0.0)))
                    
                    btn_save_emp = st.form_submit_button(t("save_emp_btn"))
                    if btn_save_emp:
                        supabase.table("employees").update({
                            "name": e_name,
                            "department": e_dept,
                            "role": e_role,
                            "total_vacation": e_tot_vac,
                            "used_vacation": e_used_vac
                        }).eq("id", selected_emp_id).execute()
                        st.success(t("save_emp_success"))
                        st.rerun()
                        
            st.dataframe(df_emps[['id', 'emp_code', 'name', 'department', 'email', 'role', 'total_vacation', 'used_vacation']], use_container_width=True, hide_index=True)
