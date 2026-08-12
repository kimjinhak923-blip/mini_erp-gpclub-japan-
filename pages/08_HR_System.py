import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t

# 1. 로그인 필수 및 페이지 설정
st.set_page_config(page_title=t("hr_title"), page_icon="⏰", layout="wide")
require_auth()

user = st.session_state["user"]
user_id = user["id"]
user_name = user["name"]
user_role = user.get("role", "EMPLOYEE")  # 'ADMIN' 또는 'EMPLOYEE'

st.title(f"⏰ {t('hr_title')} ({user_name})")

# -------------------------------------------------------------------
# [공통 1] 본인 출퇴근 체크 모듈
# -------------------------------------------------------------------
st.subheader(f"📍 {t('today_clock')}")

today = date.today().isoformat()
now_time = datetime.now().strftime("%H:%M:%S")

# 당일 출퇴근 기록 조회
attendance_res = supabase.table("attendance_logs") \
    .select("*") \
    .eq("employee_id", user_id) \
    .eq("work_date", today) \
    .execute()

today_log = attendance_res.data[0] if attendance_res.data else None

col_in, col_out, col_status = st.columns([1, 1, 2])

with col_in:
    clock_in_time = today_log["clock_in"] if today_log and today_log.get("clock_in") else t("not_checked")
    st.metric(t("clock_in_time"), clock_in_time)
    if not today_log or not today_log.get("clock_in"):
        if st.button(t("clock_in_btn"), use_container_width=True, type="primary"):
            supabase.table("attendance_logs").insert({
                "employee_id": user_id,
                "work_date": today,
                "clock_in": now_time,
                "status": "PRESENT"
            }).execute()
            st.success(f"{now_time} {t('clock_in_success')}")
            st.rerun()

with col_out:
    clock_out_time = today_log["clock_out"] if today_log and today_log.get("clock_out") else t("not_checked")
    st.metric(t("clock_out_time"), clock_out_time)
    if today_log and today_log.get("clock_in") and not today_log.get("clock_out"):
        if st.button(t("clock_out_btn"), use_container_width=True):
            supabase.table("attendance_logs").update({
                "clock_out": now_time
            }).eq("id", today_log["id"]).execute()
            st.success(f"{now_time} {t('clock_out_success')}")
            st.rerun()

with col_status:
    status_text = today_log["status"] if today_log else t("not_clocked_in")
    st.info(f"💡 {t('current_status')}: **{status_text}** ({t('today_date')}: {today})")

st.markdown("---")

# -------------------------------------------------------------------
# [공통 2] 개인별 월별 근태 캘린더
# -------------------------------------------------------------------
st.subheader(f"📅 {t('my_calendar')}")

# 이번 달 내 출퇴근 기록 조회
logs_res = supabase.table("attendance_logs") \
    .select("*") \
    .eq("employee_id", user_id) \
    .execute()

if logs_res.data:
    df_my_logs = pd.DataFrame(logs_res.data)
    
    # 캘린더 시각화용 데이터 가공 및 컬럼 다국어화
    df_calendar = df_my_logs[['work_date', 'clock_in', 'clock_out', 'status']].copy()
    df_calendar.columns = [t('col_date'), t('col_clock_in'), t('col_clock_out'), t('col_status')]
    
    st.dataframe(df_calendar, use_container_width=True, hide_index=True)
else:
    st.write(t("no_logs"))

st.markdown("---")

# -------------------------------------------------------------------
# [관리자 전용] 탭 1: 전체 직원 근태 종합 관리 / 탭 2: 신규 직원 계정 생성 및 배포
# -------------------------------------------------------------------
if user_role == "ADMIN":
    st.subheader(f"👑 {t('admin_menu')}")
    admin_tab1, admin_tab2 = st.tabs([t("tab_all_attendance"), t("tab_create_account")])

    # --- 탭 1: 전체 직원 근태 수정/삭제 ---
    with admin_tab1:
        all_logs = supabase.table("attendance_logs") \
            .select("id, work_date, clock_in, clock_out, status, employees(name, emp_code, department)") \
            .execute()
        
        if all_logs.data:
            formatted_logs = []
            for item in all_logs.data:
                emp = item.get("employees") or {}
                formatted_logs.append({
                    "log_id": item["id"],
                    t("col_date"): item["work_date"],
                    t("col_emp_code"): emp.get("emp_code", "-"),
                    t("col_name"): emp.get("name", "-"),
                    t("col_dept"): emp.get("department", "-"),
                    t("col_clock_in"): item.get("clock_in"),
                    t("col_clock_out"): item.get("clock_out"),
                    t("col_status"): item.get("status")
                })
            df_all = pd.DataFrame(formatted_logs)
            
            # 수정할 데이터 선택
            selected_log_id = st.selectbox(t("select_log_edit"), df_all["log_id"].tolist())
            
            if selected_log_id:
                target_log = df_all[df_all["log_id"] == selected_log_id].iloc[0]
                with st.form("edit_attendance_form"):
                    col_e1, col_e2, col_e3 = st.columns(3)
                    new_in = col_e1.text_input(t("col_clock_in"), value=str(target_log[t("col_clock_in")] or ""))
                    new_out = col_e2.text_input(t("col_clock_out"), value=str(target_log[t("col_clock_out")] or ""))
                    new_status = col_e3.selectbox(t("col_status"), ["PRESENT", "LATE", "ABSENT", "LEAVE"], index=0)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    save_btn = col_btn1.form_submit_button(t("save_edit"))
                    delete_btn = col_btn2.form_submit_button(t("delete_btn"), type="primary")
                    
                    if save_btn:
                        supabase.table("attendance_logs").update({
                            "clock_in": new_in if new_in else None,
                            "clock_out": new_out if new_out else None,
                            "status": new_status
                        }).eq("id", selected_log_id).execute()
                        st.success(t("edit_success"))
                        st.rerun()
                        
                    if delete_btn:
                        supabase.table("attendance_logs").delete().eq("id", selected_log_id).execute()
                        st.warning(t("delete_success"))
                        st.rerun()

            st.dataframe(df_all, use_container_width=True, hide_index=True)

    # --- 탭 2: 직원 신규 등록 및 계정 배포 ---
    with admin_tab2:
        st.markdown(f"##### {t('create_emp_header')}")
        with st.form("create_employee_form"):
            col_a1, col_a2 = st.columns(2)
            emp_code = col_a1.text_input(t("emp_code_placeholder"), placeholder="EMP-0002")
            name = col_a2.text_input(t("emp_name_label"), placeholder="홍길동")
            
            col_b1, col_b2 = st.columns(2)
            department = col_b1.text_input(t("dept_label"), placeholder="영업팀")
            position = col_b2.text_input(t("pos_label"), placeholder="대리")
            
            col_c1, col_c2 = st.columns(2)
            email = col_c1.text_input(t("login_email_label"), placeholder="user2@company.com")
            role = col_c2.selectbox(t("role_label"), ["EMPLOYEE", "ADMIN"])
            
            submit_emp = st.form_submit_button(t("create_emp_btn"), type="primary")
            
            if submit_emp:
                if not emp_code or not name or not email:
                    st.error(t("required_fields_error"))
                else:
                    try:
                        supabase.table("employees").insert({
                            "emp_code": emp_code,
                            "name": name,
                            "department": department,
                            "position": position,
                            "email": email,
                            "role": role,
                            "is_active": True
                        }).execute()
                        st.success(f"{t('account_created_success')} {email}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('account_created_error')} {e}")

        st.markdown(f"##### {t('all_emp_list')}")
        emp_list_res = supabase.table("employees").select("emp_code, name, department, position, email, role, is_active").execute()
        if emp_list_res.data:
            df_emp = pd.DataFrame(emp_list_res.data)
            df_emp.columns = [t('col_emp_code'), t('col_name'), t('col_dept'), t('col_position'), t('col_email'), t('col_role'), t('col_active')]
            st.dataframe(df_emp, use_container_width=True, hide_index=True)
else:
    st.info(t("admin_only_info"))
