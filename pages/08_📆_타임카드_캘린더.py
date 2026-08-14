import calendar
import datetime
import io
import pandas as pd
import streamlit as st

# 사이드바 예외 처리 (사이드바 파일 문제로 인한 오류 방지)
try:
    from sidebar_menu import render_sidebar
    render_sidebar()
except Exception:
    pass

st.set_page_config(page_title="타임카드 및 사내 캘린더", layout="wide")
st.title("📅 타임카드 관리 및 스케줄/사내 캘린더")
st.markdown("---")

# ==========================================
# 1. 세션 상태(Session State) 강제 초기화
# ==========================================
today = datetime.date.today()
if "tc_year" not in st.session_state:
    st.session_state.tc_year = today.year
if "tc_month" not in st.session_state:
    st.session_state.tc_month = today.month

if "users" not in st.session_state:
    st.session_state.users = [
        {"name": "관리자", "role": "admin"},
        {"name": "김사원", "role": "user"},
        {"name": "이대리", "role": "user"},
    ]

# 로그인 유저 체크
logged_user = st.session_state.get("logged_in_user", {"name": "관리자", "role": "admin"})
is_admin = (logged_user.get("role") == "admin")

# 선택된 관리/조회 대상 유저 세션 관리
if "selected_target_user" not in st.session_state:
    st.session_state.selected_target_user = logged_user["name"]

# 일반 직원은 무조건 본인 계정으로 고정
if not is_admin:
    st.session_state.selected_target_user = logged_user["name"]

# 연차/휴가 데이터
if "user_vacation_info" not in st.session_state:
    st.session_state.user_vacation_info = {
        "관리자": {"granted": 15.0, "used": 2.0},
        "김사원": {"granted": 15.0, "used": 1.0},
        "이대리": {"granted": 15.0, "used": 0.0},
    }

# 근태/타임카드 원본 데이터 (세부 항목 전체 풀 세트)
if "attendance_logs" not in st.session_state:
    st.session_state.attendance_logs = [
        {
            "user_name": "관리자", "date": "2026-08-03",
            "clock_in": "08:50", "clock_out": "18:30",
            "work_hours": 8.0, "overtime_hours": 0.5, "break_hours": 1.0,
            "late_minutes": 0, "early_leave_minutes": 0,
            "late": False, "early_leave": False,
            "status": "정상근무", "note": ""
        },
        {
            "user_name": "김사원", "date": "2026-08-03",
            "clock_in": "09:20", "clock_out": "18:00",
            "work_hours": 7.67, "overtime_hours": 0.0, "break_hours": 1.0,
            "late_minutes": 20, "early_leave_minutes": 0,
            "late": True, "early_leave": False,
            "status": "지각", "note": "교통 체증"
        },
        {
            "user_name": "김사원", "date": "2026-08-05",
            "clock_in": "09:00", "clock_out": "16:30",
            "work_hours": 6.5, "overtime_hours": 0.0, "break_hours": 1.0,
            "late_minutes": 0, "early_leave_minutes": 90,
            "late": False, "early_leave": True,
            "status": "조퇴", "note": "병원 진료"
        },
        {
            "user_name": "이대리", "date": "2026-08-04",
            "clock_in": "08:45", "clock_out": "20:00",
            "work_hours": 8.0, "overtime_hours": 2.0, "break_hours": 1.0,
            "late_minutes": 0, "early_leave_minutes": 0,
            "late": False, "early_leave": False,
            "status": "연장근무", "note": "프로젝트 마감"
        },
    ]

# 사내 공유 일정 데이터
if "company_schedules" not in st.session_state:
    st.session_state.company_schedules = [
        {"id": 1, "creator": "김사원", "date": "2026-08-05", "time": "14:00~15:30", "title": "A상사 외부 미팅", "category": "외부미팅"},
        {"id": 2, "creator": "이대리", "date": "2026-08-12", "time": "10:00~11:00", "title": "대회의실 신제품 회의", "category": "회의실사용"},
    ]

# 휴가 신청 및 승인 이력
if "schedule_requests" not in st.session_state:
    st.session_state.schedule_requests = [
        {
            "id": 1,
            "user_name": "김사원",
            "date": "2026-08-10",
            "type": "연차/휴가",
            "start_time": "-",
            "end_time": "-",
            "reason": "개인 사유 휴가",
            "status": "승인완료",
            "deducted": True,
        },
        {
            "id": 2,
            "user_name": "이대리",
            "date": "2026-08-14",
            "type": "오전반차",
            "start_time": "09:00",
            "end_time": "13:00",
            "reason": "건강검진",
            "status": "대기중",
            "deducted": False,
        }
    ]

# ==========================================
# 2. ⏱️ 정밀 시간 계산 보조 함수
# ==========================================
def calculate_attendance_details(clock_in_str, clock_out_str, break_hrs=1.0, std_in="09:00", std_out="18:00"):
    """출퇴근 시간을 파싱하여 근무시간, 잔업시간, 지각(분), 조퇴(분)를 정확하게 계산"""
    try:
        if not clock_in_str or not clock_out_str or clock_in_str.strip() == "-" or clock_out_str.strip() == "-":
            return 0.0, 0.0, 0, 0, False, False

        t_in = datetime.datetime.strptime(clock_in_str.strip(), "%H:%M")
        t_out = datetime.datetime.strptime(clock_out_str.strip(), "%H:%M")
        t_std_in = datetime.datetime.strptime(std_in, "%H:%M")
        t_std_out = datetime.datetime.strptime(std_out, "%H:%M")

        if t_out <= t_in:
            return 0.0, 0.0, 0, 0, False, False

        # 지각 계산 (분 단위)
        late_mins = max(0, int((t_in - t_std_in).total_seconds() // 60)) if t_in > t_std_in else 0
        is_late = late_mins > 0

        # 조퇴 계산 (분 단위)
        early_mins = max(0, int((t_std_out - t_out).total_seconds() // 60)) if t_out < t_std_out else 0
        is_early = early_mins > 0

        # 근무시간 & 잔업시간 계산 (휴식시간 제함)
        diff_hrs = (t_out - t_in).total_seconds() / 3600.0
        actual_work = max(0.0, diff_hrs - break_hrs)

        if actual_work > 8.0:
            work_hrs = 8.0
            overtime_hrs = actual_work - 8.0
        else:
            work_hrs = actual_work
            overtime_hrs = 0.0

        return round(work_hrs, 2), round(overtime_hrs, 2), late_mins, early_mins, is_late, is_early
    except Exception:
        return 0.0, 0.0, 0, 0, False, False

# ==========================================
# 3. 계정 권한 제어 & 대상 선택 드롭다운
# ==========================================
user_list = [u["name"] for u in st.session_state.users]

def on_target_user_change():
    st.session_state.selected_target_user = st.session_state.sel_user_key

if is_admin:
    col_adm1, col_adm2 = st.columns([2, 3])
    with col_adm1:
        current_idx = user_list.index(st.session_state.selected_target_user) if st.session_state.selected_target_user in user_list else 0
        st.selectbox(
            "👤 [관리자] 타임카드/근태 조회 및 수정 대상 선택",
            user_list,
            index=current_idx,
            key="sel_user_key",
            on_change=on_target_user_change
        )
    with col_adm2:
        st.info(f"🔑 관리자 권한 활성화: 현재 **[{st.session_state.selected_target_user}]** 님의 타임카드를 관리하고 있습니다.")
else:
    st.success(f"👤 **[{logged_user['name']}]** 님의 개인 타임카드 및 스케줄 화면입니다.")

target_user = st.session_state.selected_target_user

# 연차 현황 데이터
if target_user not in st.session_state.user_vacation_info:
    st.session_state.user_vacation_info[target_user] = {"granted": 15.0, "used": 0.0}

v_info = st.session_state.user_vacation_info[target_user]
rem_vacation = v_info["granted"] - v_info["used"]

st.markdown(
    f"💡 **[{target_user}] 님 연차 요약:** 총 부여 `{v_info['granted']}일` | 사용 `{v_info['used']}일` | **잔여 `{rem_vacation}일`**"
)

# ==========================================
# 4. ◀️ 이전달 / 다음달 ▶️ 컨트롤 툴바
# ==========================================
st.markdown("---")
c_prev, c_y, c_m, c_next, c_act1, c_act2, c_act3 = st.columns([0.8, 1, 1, 0.8, 2, 2, 2])

with c_prev:
    if st.button("◀ 이전달", use_container_width=True):
        if st.session_state.tc_month == 1:
            st.session_state.tc_month = 12
            st.session_state.tc_year -= 1
        else:
            st.session_state.tc_month -= 1
        st.rerun()

with c_y:
    st.session_state.tc_year = st.number_input("연도", value=st.session_state.tc_year, step=1, label_visibility="collapsed")

with c_m:
    st.session_state.tc_month = st.number_input("월", value=st.session_state.tc_month, min_value=1, max_value=12, step=1, label_visibility="collapsed")

with c_next:
    if st.button("다음달 ▶", use_container_width=True):
        if st.session_state.tc_month == 12:
            st.session_state.tc_month = 1
            st.session_state.tc_year += 1
        else:
            st.session_state.tc_month += 1
        st.rerun()

year = st.session_state.tc_year
month = st.session_state.tc_month

# [관리자 전용] 당일 휴가/근태 대리 즉시 수정
with c_act1:
    if is_admin:
        with st.popover(f"⚡ [{target_user}] 대리 등록 / 수정", use_container_width=True):
            st.subheader(f"🛠️ [{target_user}] 근태 관리자 즉시 수정")
            st.caption("당일 개인 사정 휴가/지각/조퇴 등 직원이 직접 등록하지 못한 경우 관리자가 즉시 처리합니다.")
            
            with st.form("admin_quick_fix_form"):
                q_date = st.date_input("대상 날짜", datetime.date.today())
                q_type = st.selectbox("구분", ["연차/휴가", "오전반차", "오후반차", "출/퇴근 직접입력", "지각/조퇴 처리", "결근"])
                
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    q_in = st.text_input("출근시간 (HH:MM)", value="09:00")
                with col_q2:
                    q_out = st.text_input("퇴근시간 (HH:MM)", value="18:00")
                
                q_break = st.number_input("휴식시간(시간)", value=1.0, step=0.5)
                q_note = st.text_area("사유/비고", value="관리자 대리 수정")

                if st.form_submit_button("⚡ 반영하기", type="primary"):
                    d_str = str(q_date)
                    
                    if "연차" in q_type or "휴가" in q_type:
                        st.session_state.user_vacation_info[target_user]["used"] += 1.0
                    elif "반차" in q_type:
                        st.session_state.user_vacation_info[target_user]["used"] += 0.5

                    calc_w, calc_o, l_m, e_m, is_l, is_e = calculate_attendance_details(q_in, q_out, q_break)

                    att = next((a for a in st.session_state.attendance_logs if a["date"] == d_str and a.get("user_name") == target_user), None)
                    
                    if att:
                        att["clock_in"] = q_in
                        att["clock_out"] = q_out
                        att["work_hours"] = calc_w
                        att["overtime_hours"] = calc_o
                        att["break_hours"] = q_break
                        att["late_minutes"] = l_m
                        att["early_leave_minutes"] = e_m
                        att["late"] = is_l
                        att["early_leave"] = is_e
                        att["status"] = q_type
                        att["note"] = q_note
                    else:
                        st.session_state.attendance_logs.append({
                            "user_name": target_user,
                            "date": d_str,
                            "clock_in": q_in,
                            "clock_out": q_out,
                            "work_hours": calc_w,
                            "overtime_hours": calc_o,
                            "break_hours": q_break,
                            "late_minutes": l_m,
                            "early_leave_minutes": e_m,
                            "late": is_l,
                            "early_leave": is_e,
                            "status": q_type,
                            "note": q_note
                        })
                    st.success(f"[{target_user}] 님의 {d_str} 근태가 정상 반영되었습니다.")
                    st.rerun()

# [공통] 사내 공유 일정 생성 / 상세 수정 / 삭제
with c_act2:
    with st.popover("📌 사내 공유 일정 관리", use_container_width=True):
        st.subheader("📌 사내 공유 일정 관리")
        tab_cs1, tab_cs2 = st.tabs(["✏️ 기존 일정 상세 수정 / 삭제", "➕ 신규 일정 생성"])

        with tab_cs1:
            if not st.session_state.company_schedules:
                st.info("등록된 사내 공유 일정이 없습니다.")
            else:
                cs_map = {f"[{s['date']}] {s['creator']}: {s['title']}": s["id"] for s in st.session_state.company_schedules}
                sel_cs_key = st.selectbox("수정/삭제할 일정 선택", list(cs_map.keys()))
                t_id = cs_map[sel_cs_key]
                t_item = next(s for s in st.session_state.company_schedules if s["id"] == t_id)

                try:
                    init_d = datetime.datetime.strptime(t_item["date"], "%Y-%m-%d").date()
                except Exception:
                    init_d = datetime.date.today()

                with st.form("edit_cs_form_cal"):
                    e_d = st.date_input("일정 날짜", init_d)
                    cat_list = ["외부미팅", "회의실사용", "업무일정", "기타"]
                    cur_cat_idx = cat_list.index(t_item.get("category", "기타")) if t_item.get("category", "기타") in cat_list else 3
                    e_cat = st.selectbox("카테고리", cat_list, index=cur_cat_idx)
                    e_time = st.text_input("시간 (예: 10:00~12:00)", value=t_item["time"])
                    e_title = st.text_input("일정 제목", value=t_item["title"])

                    c_sv, c_dl = st.columns(2)
                    with c_sv:
                        if st.form_submit_button("💾 수정사항 저장", type="primary"):
                            t_item["date"] = str(e_d)
                            t_item["category"] = e_cat
                            t_item["time"] = e_time
                            t_item["title"] = e_title
                            st.success("일정이 수정되었습니다.")
                            st.rerun()
                    with c_dl:
                        if st.form_submit_button("🗑️ 해당 일정 삭제"):
                            st.session_state.company_schedules = [s for s in st.session_state.company_schedules if s["id"] != t_id]
                            st.success("일정이 삭제되었습니다.")
                            st.rerun()

        with tab_cs2:
            with st.form("add_cs_form_cal"):
                n_d = st.date_input("날짜", datetime.date.today())
                n_cat = st.selectbox("구분", ["외부미팅", "회의실사용", "업무일정", "기타"])
                n_time = st.text_input("시간", "14:00~15:00")
                n_title = st.text_input("제목")
                if st.form_submit_button("신규 등록"):
                    new_id = max([s["id"] for s in st.session_state.company_schedules], default=0) + 1
                    st.session_state.company_schedules.append({
                        "id": new_id, "creator": logged_user["name"], "date": str(n_d),
                        "time": n_time, "title": n_title, "category": n_cat
                    })
                    st.success("새로운 일정이 등록되었습니다.")
                    st.rerun()

# [일반/관리자 공통] 휴가/근태 신청 팝업
with c_act3:
    with st.popover("📝 연차 / 근태 신청", use_container_width=True):
        st.subheader("📝 연차 및 근태 신청")
        with st.form("req_vacation_form"):
            req_d = st.date_input("신청 날짜", datetime.date.today())
            req_t = st.selectbox("신청 종류", ["연차/휴가", "오전반차", "오후반차", "외출", "조퇴"])
            req_st = st.text_input("시작시간 (반차/외출시)", "-")
            req_et = st.text_input("종료시간 (반차/외출시)", "-")
            req_r = st.text_area("신청 사유", "")

            if st.form_submit_button("신청서 제출", type="primary"):
                new_req_id = max([r["id"] for r in st.session_state.schedule_requests], default=0) + 1
                st.session_state.schedule_requests.append({
                    "id": new_req_id,
                    "user_name": target_user,
                    "date": str(req_d),
                    "type": req_t,
                    "start_time": req_st,
                    "end_time": req_et,
                    "reason": req_r,
                    "status": "대기중",
                    "deducted": False
                })
                st.success("근태/휴가 신청이 완료되었습니다.")
                st.rerun()

# ==========================================
# 5. 📊 근태 통계 대시보드 (KPI 카드 섹션)
# ==========================================
weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
_, last_day = calendar.monthrange(year, month)

# 해당 월 근태 통계 집계
user_logs_month = [
    a for a in st.session_state.attendance_logs 
    if a.get("user_name") == target_user and a["date"].startswith(f"{year}-{month:02d}")
]

total_work_days = len([a for a in user_logs_month if a.get("clock_in") and a.get("clock_in") != "-"])
total_work_hours = sum([a.get("work_hours", 0.0) for a in user_logs_month])
total_overtime_hours = sum([a.get("overtime_hours", 0.0) for a in user_logs_month])
total_late_count = len([a for a in user_logs_month if a.get("late") or a.get("late_minutes", 0) > 0])
total_early_count = len([a for a in user_logs_month if a.get("early_leave") or a.get("early_leave_minutes", 0) > 0])

st.markdown("##### 📊 월간 근태 통계 요약")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("총 근무일수", f"{total_work_days} 일")
m2.metric("총 근무시간", f"{total_work_hours:.1f} 시간")
m3.metric("연장(잔업)시간", f"{total_overtime_hours:.1f} 시간")
m4.metric("지각 횟수", f"{total_late_count} 회")
m5.metric("조퇴 횟수", f"{total_early_count} 회")

# ==========================================
# 6. 📅 캘린더 뷰 (2종 완전 분리 선택)
# ==========================================
st.markdown("---")
st.subheader(f"📅 {year}년 {month}월 캘린더")

cal_mode = st.selectbox(
    "🔄 캘린더 모드 선택 (원하시는 캘린더 화면을 선택하세요)",
    ["1️⃣ 근무 / 근태 확인 캘린더 (출퇴근·근무시간·지각/조퇴)", "2️⃣ 사내 일정 확인 캘린더 (미팅·회의실·업무스케줄)"]
)

first_weekday, _ = calendar.monthrange(year, month)

# 1️⃣ 근무/근태 확인 캘린더
if "1️⃣" in cal_mode:
    st.info(f"💡 **[{target_user}]** 님의 출퇴근 시간, 근무시간, 잔업시간 및 지각/조퇴(분) 현황을 확인합니다.")
    cols = st.columns(7)
    for idx, day_name in enumerate(weekdays_kr):
        cols[idx].markdown(f"**<center>{day_name}</center>**", unsafe_allow_html=True)

    day_counter = 1
    for week in range(6):
        if day_counter > last_day:
            break
        grid_cols = st.columns(7)
        for idx in range(7):
            if (week == 0 and idx < first_weekday) or day_counter > last_day:
                grid_cols[idx].write(" ")
            else:
                curr_d_str = f"{year}-{month:02d}-{day_counter:02d}"
                att_day = next((a for a in st.session_state.attendance_logs if a["date"] == curr_d_str and a.get("user_name") == target_user), None)

                box_content = f"**{day_counter}일**\n\n"
                if att_day:
                    box_content += f"⏰ `{att_day.get('clock_in','-')}~{att_day.get('clock_out','-')}`\n"
                    box_content += f"⏱️ 근무: `{att_day.get('work_hours', 0.0)}h` (잔업 `{att_day.get('overtime_hours', 0.0)}h`)\n"
                    
                    if att_day.get("late_minutes", 0) > 0:
                        box_content += f"⚠️ `지각 {att_day.get('late_minutes')}분` "
                    if att_day.get("early_leave_minutes", 0) > 0:
                        box_content += f"⚠️ `조퇴 {att_day.get('early_leave_minutes')}분` "
                    if att_day.get("status") and att_day.get("status") != "정상근무":
                        box_content += f"\n🏷️ `{att_day.get('status')}`"
                    box_content += "\n"
                else:
                    box_content += "─\n"

                grid_cols[idx].info(box_content)
                day_counter += 1

# 2️⃣ 사내 일정 확인 캘린더
else:
    cat_filter = st.multiselect("📌 일정 카테고리 필터", ["외부미팅", "회의실사용", "업무일정", "기타"], default=["외부미팅", "회의실사용", "업무일정", "기타"])
    cols = st.columns(7)
    for idx, day_name in enumerate(weekdays_kr):
        cols[idx].markdown(f"**<center>{day_name}</center>**", unsafe_allow_html=True)

    day_counter = 1
    for week in range(6):
        if day_counter > last_day:
            break
        grid_cols = st.columns(7)
        for idx in range(7):
            if (week == 0 and idx < first_weekday) or day_counter > last_day:
                grid_cols[idx].write(" ")
            else:
                curr_d_str = f"{year}-{month:02d}-{day_counter:02d}"
                sch_day = [s for s in st.session_state.company_schedules if s["date"] == curr_d_str and s.get("category", "기타") in cat_filter]

                box_content = f"**{day_counter}일**\n\n"
                if sch_day:
                    for sch in sch_day:
                        box_content += f"📌 [{sch.get('category')}] {sch['title']} ({sch['time']})\n"
                else:
                    box_content += "─\n"

                grid_cols[idx].success(box_content)
                day_counter += 1

# ==========================================
# 7. 📋 상세 타임카드 테이블 & 직관적 수정 모듈
# ==========================================
st.markdown("---")
st.subheader(f"📋 [{target_user}] 님 상세 타임카드 (근무·잔업·지각/조퇴 분단위 세부 내역)")

daily_data = []
for d in range(1, last_day + 1):
    curr_date = datetime.date(year, month, d)
    date_str = curr_date.strftime("%Y-%m-%d")
    date_disp = f"{month}/{d}({weekdays_kr[curr_date.weekday()]})"

    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == target_user), None)

    daily_data.append({
        "raw_date": date_str,
        "날짜": date_disp,
        "출근시간": att.get("clock_in", "-") if att else "-",
        "퇴근시간": att.get("clock_out", "-") if att else "-",
        "근무시간(h)": att.get("work_hours", 0.0) if att else 0.0,
        "잔업시간(h)": att.get("overtime_hours", 0.0) if att else 0.0,
        "지각(분)": att.get("late_minutes", 0) if att else 0,
        "조퇴(분)": att.get("early_leave_minutes", 0) if att else 0,
        "휴식시간(h)": att.get("break_hours", 1.0) if att else 1.0,
        "상태": att.get("status", "미기록") if att else "미기록",
        "비고/사유": att.get("note", "") if att else ""
    })

df_tc = pd.DataFrame(daily_data)

st.dataframe(
    df_tc[["날짜", "출근시간", "퇴근시간", "근무시간(h)", "잔업시간(h)", "지각(분)", "조퇴(분)", "휴식시간(h)", "상태", "비고/사유"]],
    use_container_width=True,
    height=360
)

# [관리자 전용] 직관적 시스템 관리 스타일 수정 모듈
if is_admin:
    st.markdown("##### 🛠️ [관리자] 직관적 1:1 타임카드 수정 및 자동 계산")
    st.caption("시스템 관리 페이지처럼 수정할 일자를 선택한 후 출/퇴근 시간을 변경하면 근무/잔업시간 및 지각/조퇴(분)가 실시간 자동 계산되어 원본에 저장됩니다.")

    with st.form("admin_simple_edit_form"):
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
            sel_edit_date = st.date_input("수정할 날짜 선택", datetime.date(year, month, 1))
        
        target_d_str = str(sel_edit_date)
        cur_att = next((a for a in st.session_state.attendance_logs if a["date"] == target_d_str and a.get("user_name") == target_user), {})

        with col_e2:
            edit_in = st.text_input("출근시간 (HH:MM)", value=cur_att.get("clock_in", "09:00"))
        with col_e3:
            edit_out = st.text_input("퇴근시간 (HH:MM)", value=cur_att.get("clock_out", "18:00"))
        with col_e4:
            edit_break = st.number_input("휴식시간 (시간)", value=cur_att.get("break_hours", 1.0), step=0.5)

        col_e5, col_e6, col_e7 = st.columns([2, 2, 2])
        with col_e5:
            edit_status = st.selectbox("근태 상태", ["정상근무", "지각", "조퇴", "연장근무", "연차/휴가", "반차", "결근"], index=0)
        with col_e6:
            edit_note = st.text_input("비고/사유", value=cur_att.get("note", ""))
        with col_e7:
            st.write(" ")
            st.write(" ")
            submit_edit = st.form_submit_button("💾 타임카드 수정 저장", type="primary", use_container_width=True)

        if submit_edit:
            w_hrs, o_hrs, l_mins, e_mins, is_l, is_e = calculate_attendance_details(edit_in, edit_out, edit_break)
            
            att_item = next((a for a in st.session_state.attendance_logs if a["date"] == target_d_str and a.get("user_name") == target_user), None)
            
            if att_item:
                att_item["clock_in"] = edit_in
                att_item["clock_out"] = edit_out
                att_item["work_hours"] = w_hrs
                att_item["overtime_hours"] = o_hrs
                att_item["late_minutes"] = l_mins
                att_item["early_leave_minutes"] = e_mins
                att_item["late"] = is_l
                att_item["early_leave"] = is_e
                att_item["break_hours"] = edit_break
                att_item["status"] = edit_status
                att_item["note"] = edit_note
            else:
                st.session_state.attendance_logs.append({
                    "user_name": target_user,
                    "date": target_d_str,
                    "clock_in": edit_in,
                    "clock_out": edit_out,
                    "work_hours": w_hrs,
                    "overtime_hours": o_hrs,
                    "late_minutes": l_mins,
                    "early_leave_minutes": e_mins,
                    "late": is_l,
                    "early_leave": is_e,
                    "break_hours": edit_break,
                    "status": edit_status,
                    "note": edit_note
                })
            st.success(f"[{target_user}] 님의 {target_d_str} 타임카드가 정밀 수정되었습니다! (지각: {l_mins}분 / 조퇴: {e_mins}분 / 근무: {w_hrs}h 자동계산 반영 완료)")
            st.rerun()

# CSV 내보내기 버튼
csv_data = df_tc[["날짜", "출근시간", "퇴근시간", "근무시간(h)", "잔업시간(h)", "지각(분)", "조퇴(분)", "휴식시간(h)", "상태", "비고/사유"]].to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 타임카드 CSV 내보내기",
    data=csv_data,
    file_name=f"{target_user}_타임카드_{year}_{month}.csv",
    mime="text/csv"
)

# ==========================================
# 8. 📑 휴가/근태 신청 이력 및 결재 관리자 승인
# ==========================================
st.markdown("---")
st.subheader(f"📑 [{target_user}] 님 휴가/근태 신청 이력 및 결재 현황")

user_reqs = [r for r in st.session_state.schedule_requests if r.get("user_name") == target_user]

if user_reqs:
    df_reqs = pd.DataFrame(user_reqs)
    st.dataframe(
        df_reqs[["date", "type", "reason", "status"]].rename(columns={
            "date": "신청일자", "type": "구분", "reason": "사유", "status": "승인상태"
        }),
        use_container_width=True
    )
else:
    st.caption("등록된 휴가/근태 신청 이력이 없습니다.")

# 관리자 전용 미승인 결재 처리 세션
if is_admin:
    pending_reqs = [r for r in st.session_state.schedule_requests if r["status"] in ["대기중", "승인대기"]]
    if pending_reqs:
        st.markdown("##### ⚡ 관리자 미승인 결재 대기 건 처리")
        for p_req in pending_reqs:
            col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
            col_p1.write(f"📌 **[{p_req['user_name']}]** {p_req['date']} - {p_req['type']} ({p_req['reason']})")
            if col_p2.button("✅ 승인", key=f"app_ok_{p_req['id']}"):
                p_req["status"] = "승인완료"
                if "연차" in p_req["type"]:
                    st.session_state.user_vacation_info[p_req['user_name']]["used"] += 1.0
                elif "반차" in p_req["type"]:
                    st.session_state.user_vacation_info[p_req['user_name']]["used"] += 0.5
                st.success("승인 처리되었습니다.")
                st.rerun()
            if col_p3.button("❌ 반려", key=f"app_no_{p_req['id']}"):
                p_req["status"] = "반려"
                st.warning("반려 처리되었습니다.")
                st.rerun()
