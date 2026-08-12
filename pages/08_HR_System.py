import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t

# 1. 로그인 필수 및 페이지 설정
st.set_page_config(page_title="인사 및 근태 관리", page_icon="⏰", layout="wide")
require_auth()

user = st.session_state["user"]
user_id = user["id"]
user_name = user["name"]
user_role = user.get("role", "EMPLOYEE")  # 'ADMIN' 또는 'EMPLOYEE'

st.title(f"⏰ 근태 및 인사 관리 ({user_name} 님)")

# -------------------------------------------------------------------
# [공통 1] 본인 출퇴근 체크 모듈 (로그인 직후 가장 먼저 보이는 상단 배치)
# -------------------------------------------------------------------
st.subheader("📍 오늘의 출퇴근 체크")

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
    clock_in_time = today_log["clock_in"] if today_log and today_log.get("clock_in") else "미체크"
    st.metric("출근 시간", clock_in_time)
    if not today_log or not today_log.get("clock_in"):
        if st.button("🚀 출근하기", use_container_width=True, type="primary"):
            supabase.table("attendance_logs").insert({
                "employee_id": user_id,
                "work_date": today,
                "clock_in": now_time,
                "status": "PRESENT"
            }).execute()
            st.success(f"{now_time} 출근 처리되었습니다.")
            st.rerun()

with col_out:
    clock_out_time = today_log["clock_out"] if today_log and today_log.get("clock_out") else "미체크"
    st.metric("퇴근 시간", clock_out_time)
    if today_log and today_log.get("clock_in") and not today_log.get("clock_out"):
        if st.button("🚪 퇴근하기", use_container_width=True):
            supabase.table("attendance_logs").update({
                "clock_out": now_time
            }).eq("id", today_log["id"]).execute()
            st.success(f"{now_time} 퇴근 처리되었습니다.")
            st.rerun()

with col_status:
    status_text = today_log["status"] if today_log else "미출근"
    st.info(f"💡 현재 상태: **{status_text}** (오늘 날짜: {today})")

st.markdown("---")

# -------------------------------------------------------------------
# [공통 2] 개인별 월별 근태 캘린더
# -------------------------------------------------------------------
st.subheader("📅 나의 월별 근태 캘린더")

# 이번 달 내 출퇴근 기록 조회
logs_res = supabase.table("attendance_logs") \
    .select("*") \
    .eq("employee_id", user_id) \
    .execute()

if logs_res.data:
    df_my_logs = pd.DataFrame(logs_res.data)
    
    # 캘린더 시각화용 데이터 가공
    df_calendar = df_my_logs[['work_date', 'clock_in', 'clock_out', 'status']].copy()
    df_calendar.columns = ['날짜', '출근시간', '퇴근시간', '상태']
    
    # 데이터프레임 UI 개선 (날짜별 피벗 형태 표 시각화)
    st.dataframe(df_calendar, use_container_width=True, hide_index=True)
else:
    st.write("이번 달 근태 기록이 없습니다.")

st.markdown("---")

# -------------------------------------------------------------------
# [관리자 전용] 탭 1: 전체 직원 근태 종합 관리 / 탭 2: 신규 직원 계정 생성 및 배포
# -------------------------------------------------------------------
if user_role == "ADMIN":
    st.subheader("👑 관리자 전용 인사 관리 메뉴")
    admin_tab1, admin_tab2 = st.tabs(["📊 전체 직원 근태 관리 (수정/삭제)", "👤 직원 계정 생성 및 배포"])

    # --- 탭 1: 전체 직원 근태 수정/삭제 ---
    with admin_tab1:
        st.markdown("##### 🔍 전체 직원 출퇴근 기록 조회 및 수정")
        all_logs = supabase.table("attendance_logs") \
            .select("id, work_date, clock_in, clock_out, status, employees(name, emp_code, department)") \
            .execute()
        
        if all_logs.data:
            formatted_logs = []
            for item in all_logs.data:
                emp = item.get("employees") or {}
                formatted_logs.append({
                    "log_id": item["id"],
                    "날짜": item["work_date"],
                    "사번": emp.get("emp_code", "-"),
                    "이름": emp.get("name", "-"),
                    "부서": emp.get("department", "-"),
                    "출근시간": item.get("clock_in"),
                    "퇴근시간": item.get("clock_out"),
                    "상태": item.get("status")
                })
            df_all = pd.DataFrame(formatted_logs)
            
            # 수정할 데이터 선택
            selected_log_id = st.selectbox("수정/삭제할 기록 선택 (ID)", df_all["log_id"].tolist())
            
            if selected_log_id:
                target_log = df_all[df_all["log_id"] == selected_log_id].iloc[0]
                with st.form("edit_attendance_form"):
                    col_e1, col_e2, col_e3 = st.columns(3)
                    new_in = col_e1.text_input("출근 시간", value=str(target_log["출근시간"] or ""))
                    new_out = col_e2.text_input("퇴근 시간", value=str(target_log["퇴근시간"] or ""))
                    new_status = col_e3.selectbox("상태", ["PRESENT", "LATE", "ABSENT", "LEAVE"], index=0)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    save_btn = col_btn1.form_submit_button("수정 저장")
                    delete_btn = col_btn2.form_submit_button("삭제하기", type="primary")
                    
                    if save_btn:
                        supabase.table("attendance_logs").update({
                            "clock_in": new_in if new_in else None,
                            "clock_out": new_out if new_out else None,
                            "status": new_status
                        }).eq("id", selected_log_id).execute()
                        st.success("근태 기록이 수정되었습니다.")
                        st.rerun()
                        
                    if delete_btn:
                        supabase.table("attendance_logs").delete().eq("id", selected_log_id).execute()
                        st.warning("기록이 삭제되었습니다.")
                        st.rerun()

            st.dataframe(df_all, use_container_width=True, hide_index=True)

    # --- 탭 2: 직원 신규 등록 및 계정 배포 ---
    with admin_tab2:
        st.markdown("##### ➕ 신규 직원 등록 (로그인 계정 발급)")
        with st.form("create_employee_form"):
            col_a1, col_a2 = st.columns(2)
            emp_code = col_a1.text_input("사번 (예: EMP-0002)", placeholder="EMP-0002")
            name = col_a2.text_input("직원 이름", placeholder="홍길동")
            
            col_b1, col_b2 = st.columns(2)
            department = col_b1.text_input("부서명", placeholder="영업팀")
            position = col_b2.text_input("직급", placeholder="대리")
            
            col_c1, col_c2 = st.columns(2)
            email = col_c1.text_input("로그인용 이메일", placeholder="user2@company.com")
            role = col_c2.selectbox("권한 구분", ["EMPLOYEE", "ADMIN"])
            
            submit_emp = st.form_submit_button("직원 계정 생성하기", type="primary")
            
            if submit_emp:
                if not emp_code or not name or not email:
                    st.error("사번, 이름, 이메일은 필수 입력 항목입니다.")
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
                        st.success(f"계정이 생성되었습니다! 직원 전달용 로그인 이메일: {email}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"계정 생성 실패: {e}")

        st.markdown("##### 📋 등록된 전체 직원 목록")
        emp_list_res = supabase.table("employees").select("emp_code, name, department, position, email, role, is_active").execute()
        if emp_list_res.data:
            st.dataframe(pd.DataFrame(emp_list_res.data), use_container_width=True, hide_index=True)
else:
    st.info("🔒 관리자 권한(ADMIN)으로 로그인하시면 전체 직원 근태 관리 및 신규 계정 생성 메뉴가 활성화됩니다.")
