import streamlit as st
import pandas as pd
from utils.db_client import supabase
from utils.auth import require_auth

# Streamlit 설정은 최상단에 배치
st.set_page_config(page_title="ERP System", page_icon="🏢", layout="wide")

# 로그인 인증 수행 (미인증 시 여기서 화면이 멈추고 로그인 화면 표시)
require_auth()

# --- 이 아래부터 기존 페이지 기능 코드 작성 ---

st.set_page_config(page_title="HR & Attendance", page_icon="⏰", layout="wide")
st.title("⏰ HR & Attendance Management (인사 및 근태 관리)")
st.caption("직원 출퇴근 등록, 근태 현황 추적 및 직원 마스터 관리")

tab1, tab2, tab3 = st.tabs(["⏰ 출퇴근 등록 (Clock-In / Out)", "📅 근태/출퇴근 이력 조회", "👤 직원 마스터 관리"])

# 직원 목록 로드
employees_res = supabase.table("employees").select("*").eq("is_active", True).execute()
employees = employees_res.data if employees_res.data else []
employee_dict = {f"[{emp.get('emp_code', 'EMP')}] {emp.get('name')} ({emp.get('department', '미정')})": emp for emp in employees}

# ==========================================
# 1. 실시간 출퇴근 등록
# ==========================================
with tab1:
    st.subheader("⏱️ 오늘 출퇴근 체크")
    
    if not employees:
        st.warning("⚠️ 등록된 활성 직원이 없습니다. [직원 마스터 관리] 탭에서 먼저 직원을 등록해 주세요.")
    else:
        selected_emp_label = st.selectbox("직원 선택*", list(employee_dict.keys()))
        target_emp = employee_dict[selected_emp_label]
        emp_id = target_emp["id"]
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 오늘의 근태 기록 확인
        today_log_res = supabase.table("attendance_logs").select("*").eq("employee_id", emp_id).eq("work_date", today_str).execute()
        today_log = today_log_res.data[0] if today_log_res.data else None
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"👤 선택 직원: **{target_emp['name']}** ({target_emp.get('position', '사원')})")
        with col_info2:
            st.metric("오늘 날짜", today_str)
            
        st.divider()
        col_btn1, col_btn2 = st.columns(2)
        
        # 출근 처리
        with col_btn1:
            clock_in_time = today_log.get("clock_in") if today_log else None
            if clock_in_time:
                st.success(f"✅ 출근 완료: {clock_in_time[:5] if len(clock_in_time)>=5 else clock_in_time}")
            else:
                if st.button("🚀 출근하기 (Clock In)", use_container_width=True, type="primary"):
                    now_time_str = datetime.now().strftime("%H:%M:%S")
                    try:
                        supabase.table("attendance_logs").insert({
                            "employee_id": emp_id,
                            "work_date": today_str,
                            "clock_in": now_time_str,
                            "status": "PRESENT"
                        }).execute()
                        st.success(f"출근 처리되었습니다! ({now_time_str})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"출근 처리 중 오류: {e}")
                        
        # 퇴근 처리
        with col_btn2:
            clock_out_time = today_log.get("clock_out") if today_log else None
            if clock_out_time:
                st.info(f"🏁 퇴근 완료: {clock_out_time[:5] if len(clock_out_time)>=5 else clock_out_time}")
            else:
                disabled_out = False if clock_in_time else True
                if st.button("🏁 퇴근하기 (Clock Out)", use_container_width=True, disabled=disabled_out):
                    now_time_str = datetime.now().strftime("%H:%M:%S")
                    try:
                        supabase.table("attendance_logs").update({
                            "clock_out": now_time_str
                        }).eq("id", today_log["id"]).execute()
                        st.success(f"퇴근 처리되었습니다! ({now_time_str})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"퇴근 처리 중 오류: {e}")


# ==========================================
# 2. 근태/출퇴근 이력 조회
# ==========================================
with tab2:
    st.subheader("📅 출퇴근 및 근태 기록 현황")
    
    logs_res = supabase.table("attendance_logs").select("*, employees(emp_code, name, department)").order("work_date", desc=True).execute()
    
    if logs_res.data:
        df_logs = pd.DataFrame([{
            "근무일자": log["work_date"],
            "사번": log.get("employees", {}).get("emp_code", "-") if log.get("employees") else "-",
            "이름": log.get("employees", {}).get("name", "-") if log.get("employees") else "-",
            "부서": log.get("employees", {}).get("department", "-") if log.get("employees") else "-",
            "출근시간": log.get("clock_in", "-"),
            "퇴근시간": log.get("clock_out", "-") or "근무 중",
            "상태": log.get("status", "PRESENT")
        } for log in logs_res.data])
        
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("기록된 출퇴근 이력이 없습니다.")


# ==========================================
# 3. 직원 마스터 관리
# ==========================================
with tab3:
    st.subheader("👤 신규 직원 등록 및 목록")
    
    with st.expander("➕ 신규 직원 등록하기", expanded=False):
        with st.form("add_emp_form", clear_on_submit=True):
            col_e1, col_e2, col_e3 = st.columns(3)
            emp_code = col_e1.text_input("사번*", value=f"EMP-{datetime.now().strftime('%m%d%H%M')}")
            emp_name = col_e2.text_input("직원 이름*")
            department = col_e3.selectbox("부서", ["영업부", "물류부", "IT개발부", "인사총무부", "경영지원부"])
            
            col_e4, col_e5 = st.columns(2)
            position = col_e4.selectbox("직급", ["사원", "주임", "대리", "과장", "차장", "부장", "이사"])
            email = col_e5.text_input("이메일 주소")
            
            submitted_emp = st.form_submit_button("💾 직원 등록")
            if submitted_emp:
                if not emp_name:
                    st.error("직원 이름은 필수 입력값입니다.")
                else:
                    try:
                        supabase.table("employees").insert({
                            "emp_code": emp_code,
                            "name": emp_name,
                            "department": department,
                            "position": position,
                            "email": email,
                            "is_active": True
                        }).execute()
                        st.success(f"직원 '{emp_name}'님이 등록되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"직원 등록 오류: {e}")
                        
    st.markdown("##### 📋 등록된 직원 목록")
    if employees:
        df_emp = pd.DataFrame(employees)[["emp_code", "name", "department", "position", "email", "is_active"]]
        df_emp.columns = ["사번", "이름", "부서", "직급", "이메일", "재직여부"]
        st.dataframe(df_emp, use_container_width=True)
    else:
        st.info("등록된 직원이 없습니다.")
