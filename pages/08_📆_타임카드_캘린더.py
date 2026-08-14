import calendar
import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 0. Streamlit 최상단 설정
# ==========================================
st.set_page_config(page_title="타임카드 및 사내 캘린더", layout="wide")

# 사이드바 예외 처리
try:
    from sidebar_menu import render_sidebar
    render_sidebar()
except Exception:
    pass

st.title("📅 타임카드 관리 및 스케줄/사내 캘린더")
st.markdown("---")

# ==========================================
# 1. 세션 상태(Session State) 초기화
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

# 관리/조회 대상 유저 세션
if "selected_target_user" not in st.session_state:
    st.session_state.selected_target_user = logged_user["name"]

# 연차 데이터
if "user_vacation_info" not in st.session_state:
    st.session_state.user_vacation_info = {
        "관리자": {"granted": 15.0, "used": 2.0},
        "김사원": {"granted": 15.0, "used": 1.0},
        "이대리": {"granted": 15.0, "used": 0.0},
    }

# 근태 원본 데이터
if "attendance_logs" not in st.session_state:
    st.session_state.attendance_logs = [
        {
            "user_name": "관리자", "date": "2026-08-03",
            "clock_in": "08:50", "clock_out": "18:30",
            "break_hours": 1.0, "status": "정상근무", "note": "",
            "late_mins": 0, "early_mins": 0
        },
        {
            "user_name": "김사원", "date": "2026-08-03",
            "clock_in": "09:20", "clock_out": "18:00",
            "break_hours": 1.0, "status": "지각", "note": "교통 체증",
            "late_mins": 20, "early_mins": 0
        },
        {
            "user_name": "김사원", "date": "2026-08-05",
            "clock_in": "09:00", "clock_out": "16:30",
            "break_hours": 0.0, "status": "조퇴", "note": "병원 진료",
            "late_mins": 0, "early_mins": 90
        },
        {
            "user_name": "이대리", "date": "2026-08-04",
            "clock_in": "08:45", "clock_out": "20:15",
            "break_hours": 1.0, "status": "연장근무", "note": "프로젝트 마감",
            "late_mins": 0, "early_mins": 0
        },
    ]

# 사내 공유 일정
if "company_schedules" not in st.session_state:
    st.session_state.company_schedules = [
        {"id": 1, "creator": "김사원", "date": "2026-08-05", "time": "14:00~15:30", "title": "A상사 외부 미팅", "category": "외부미팅"},
        {"id": 2, "creator": "이대리", "date": "2026-08-12", "time": "10:00~11:00", "title": "대회의실 신제품 회의", "category": "회의실사용"},
    ]

# 휴가/근태 신청 이력
if "schedule_requests" not in st.session_state:
    st.session_state.schedule_requests = [
        {
            "id": 1, "user_name": "김사원", "date": "2026-08-10",
            "type": "연차/휴가", "reason": "개인 사유 휴가", "status": "승인완료"
        },
        {
            "id": 2, "user_name": "이대리", "date": "2026-08-14",
            "type": "오전반차", "reason": "건강검진", "status": "대기중"
        }
    ]

# 인라인 수정 선택 세션
if "editing_date" not in st.session_state:
    st.session_state.editing_date = None

# 🇯🇵 일본 공휴일 마스터 데이터 연동 (예: 2026년 8월 산의 날 8/11, 대체휴일 8/12 등)
JAPAN_HOLIDAYS = [
    "2026-08-11", # 산의 날
    "2026-08-12", # 대체휴무
]

# ==========================================
# 2. ⏱️ 근무/잔업 정밀 계산 로직
# ==========================================
def calculate_work_and_overtime(clock_in_str, clock_out_str, manual_break=None, manual_late=None, manual_early=None):
    try:
        if not clock_in_str or not clock_out_str or clock_in_str.strip() in ["-", ""]:
            return 0.0, 0.0, 0, 0, 0.0, 0.0

        t_in = datetime.datetime.strptime(clock_in_str.strip(), "%H:%M")
        t_out = datetime.datetime.strptime(clock_out_str.strip(), "%H:%M")
        t_std_in = datetime.datetime.strptime("09:00", "%H:%M")
        t_std_out = datetime.datetime.strptime("18:00", "%H:%M")

        total_presence = max(0.0, (t_out - t_in).total_seconds() / 3600.0)

        if manual_break is not None and manual_break != "":
            break_hours = float(manual_break)
        else:
            break_hours = 1.00 if total_presence >= 8.0 else 0.00

        effective_in = max(t_in, t_std_in)
        effective_out = min(t_out, t_std_out)
        
        if effective_out > effective_in:
            raw_std_work = (effective_out - effective_in).total_seconds() / 3600.0
            work_hours = max(0.0, round(raw_std_work - break_hours, 2))
        else:
            work_hours = 0.0

        overtime_hours = 0.0
        if t_out > t_std_out:
            overtime_seconds = (t_out - t_std_out).total_seconds()
            overtime_hours = round(overtime_seconds / 3600.0, 2)

        total_work_hours = round(work_hours + overtime_hours, 2)

        if manual_late is not None:
            late_mins = int(manual_late)
        else:
            late_mins = max(0, int((t_in - t_std_in).total_seconds() // 60)) if t_in > t_std_in else 0

        if manual_early is not None:
            early_mins = int(manual_early)
        else:
            early_mins = max(0, int((t_std_out - t_out).total_seconds() // 60)) if t_out < t_std_out else 0

        return work_hours, overtime_hours, late_mins, early_mins, break_hours, total_work_hours
    except Exception:
        return 0.0, 0.0, 0, 0, 0.0, 0.0

# ==========================================
# 3. 👤 직원별 타임카드 선택 드롭다운 (추가/강화)
# ==========================================
user_list = [u["name"] for u in st.session_state.users]

col_sel1, col_sel2 = st.columns([2, 3])
with col_sel1:
    current_idx = user_list.index(st.session_state.selected_target_user) if st.session_state.selected_target_user in user_list else 0
    selected_user = st.selectbox(
        "👤 직원 선택 (타임카드 / 캘린더 조회 대상)",
        user_list,
        index=current_idx,
        key="target_user_selector"
    )
    st.session_state.selected_target_user = selected_user

with col_sel2:
    if is_admin:
        st.info(f"🔑 [관리자 권한] **[{st.session_state.selected_target_user}]** 님의 타임카드 및 캘린더를 조회 중입니다.")
    else:
        st.success(f"👤 **[{st.session_state.selected_target_user}]** 님의 타임카드 및 캘린더 정보입니다.")

target_user = st.session_state.selected_target_user

# 연차 정보 안전 초기화
if target_user not in st.session_state.user_vacation_info:
    st.session_state.user_vacation_info[target_user] = {"granted": 15.0, "used": 0.0}

v_info = st.session_state.user_vacation_info[target_user]
rem_vacation = v_info["granted"] - v_info["used"]

st.caption(f"💡 [{target_user}] 님 연차 현황: 총 부여 `{v_info['granted']}일` | 사용 `{v_info['used']}일` | **잔여 `{rem_vacation}일`**")

# ==========================================
# 4. ◀️ 이전달 / 다음달 ▶️ 상단 이동 툴바
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

# [관리자] 대리 수정 팝업
with c_act1:
    if is_admin:
        with st.popover(f"⚡ [{target_user}] 대리 등록", use_container_width=True):
            st.subheader(f"🛠️ [{target_user}] 관리자 대리 등록")
            with st.form("admin_quick_fix_form"):
                q_date = st.date_input("대상 날짜", datetime.date.today())
                q_type = st.selectbox("구분", ["정상근무", "연차/휴가", "오전반차", "오후반차", "지각", "조퇴", "결근"])
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    q_in = st.text_input("출근시간 (HH:MM)", value="09:00")
                with col_q2:
                    q_out = st.text_input("퇴근시간 (HH:MM)", value="18:00")
                
                col_q3, col_q4, col_q5 = st.columns(3)
                with col_q3:
                    q_break = st.number_input("휴식", value=1.0, step=0.5)
                with col_q4:
                    q_late = st.number_input("지각", value=0, step=1)
                with col_q5:
                    q_early = st.number_input("조퇴", value=0, step=1)

                q_note = st.text_area("비고/사유", value="관리자 등록")

                if st.form_submit_button("⚡ 즉시 반영", type="primary"):
                    d_str = str(q_date)
                    att = next((a for a in st.session_state.attendance_logs if a["date"] == d_str and a.get("user_name") == target_user), None)
                    if att:
                        att.update({
                            "clock_in": q_in, "clock_out": q_out,
                            "break_hours": q_break, "late_mins": q_late, "early_mins": q_early,
                            "status": q_type, "note": q_note
                        })
                    else:
                        st.session_state.attendance_logs.append({
                            "user_name": target_user, "date": d_str,
                            "clock_in": q_in, "clock_out": q_out,
                            "break_hours": q_break, "late_mins": q_late, "early_mins": q_early,
                            "status": q_type, "note": q_note
                        })
                    st.success("반영되었습니다.")
                    st.rerun()

# [공통] 사내 공유 일정 관리 팝업
with c_act2:
    with st.popover("📌 사내 공유 일정 관리", use_container_width=True):
        st.subheader("📌 사내 공유 일정 C.R.U.D")
        tab_cs1, tab_cs2 = st.tabs(["✏️ 기존 일정 수정/삭제", "➕ 신규 일정 생성"])
        
        with tab_cs1:
            if not st.session_state.company_schedules:
                st.info("등록된 일정이 없습니다.")
            else:
                cs_map = {f"[{s['date']}] {s['creator']}: {s['title']}": s["id"] for s in st.session_state.company_schedules}
                sel_cs_key = st.selectbox("수정/삭제할 일정 선택", list(cs_map.keys()))
                t_id = cs_map[sel_cs_key]
                t_item = next(s for s in st.session_state.company_schedules if s["id"] == t_id)

                with st.form("edit_cs_form_cal"):
                    e_d = st.date_input("일정 날짜", datetime.datetime.strptime(t_item["date"], "%Y-%m-%d").date())
                    cat_list = ["외부미팅", "회의실사용", "업무일정", "기타"]
                    e_cat = st.selectbox("카테고리", cat_list, index=cat_list.index(t_item.get("category", "기타")))
                    e_time = st.text_input("시간", value=t_item["time"])
                    e_title = st.text_input("제목", value=t_item["title"])

                    c_sv, c_dl = st.columns(2)
                    if c_sv.form_submit_button("💾 수정 저장", type="primary"):
                        t_item.update({"date": str(e_d), "category": e_cat, "time": e_time, "title": e_title})
                        st.success("수정되었습니다.")
                        st.rerun()
                    if c_dl.form_submit_button("🗑️ 삭제"):
                        st.session_state.company_schedules = [s for s in st.session_state.company_schedules if s["id"] != t_id]
                        st.success("삭제되었습니다.")
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
                    st.success("등록되었습니다.")
                    st.rerun()

# [공통] 휴가 및 근태 신청 팝업
with c_act3:
    with st.popover("📝 연차 / 근태 신청", use_container_width=True):
        st.subheader("📝 연차 및 근태 신청")
        with st.form("req_vacation_form"):
            req_d = st.date_input("신청 날짜", datetime.date.today())
            req_t = st.selectbox("신청 구분", ["연차/휴가", "오전반차", "오후반차", "외출", "조퇴"])
            req_r = st.text_area("신청 사유", "")
            if st.form_submit_button("신청서 제출", type="primary"):
                new_req_id = max([r["id"] for r in st.session_state.schedule_requests], default=0) + 1
                st.session_state.schedule_requests.append({
                    "id": new_req_id, "user_name": target_user, "date": str(req_d),
                    "type": req_t, "reason": req_r, "status": "대기중"
                })
                st.success("신청되었습니다.")
                st.rerun()

# ==========================================
# 5. 📊 최상단 월간 근태 통계 요약
# ==========================================
weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
_, last_day = calendar.monthrange(year, month)

tot_days = 0
tot_work_h = 0.0
tot_over_h = 0.0
tot_late_c = 0
tot_early_c = 0

for d in range(1, last_day + 1):
    d_str = f"{year}-{month:02d}-{d:02d}"
    att = next((a for a in st.session_state.attendance_logs if a["date"] == d_str and a.get("user_name") == target_user), None)
    if att and att.get("clock_in") and att.get("clock_in") != "-":
        w_h, o_h, l_m, e_m, b_h, t_w_h = calculate_work_and_overtime(
            att.get("clock_in"), att.get("clock_out"),
            att.get("break_hours"), att.get("late_mins"), att.get("early_mins")
        )
        tot_days += 1
        tot_work_h += t_w_h
        tot_over_h += o_h
        if l_m > 0 or att.get("status") == "지각":
            tot_late_c += 1
        if e_m > 0 or att.get("status") == "조퇴":
            tot_early_c += 1

st.markdown(f"##### 📊 [{target_user}] 님 {year}년 {month}월 근태 통계 요약")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("총 근무일수", f"{tot_days} 일")
m2.metric("총 근무시간", f"{tot_work_h:.2f} 시간")
m3.metric("연장(잔업)시간", f"{tot_over_h:.2f} 시간")
m4.metric("지각 횟수", f"{tot_late_c} 회")
m5.metric("조퇴 횟수", f"{tot_early_c} 회")

# ==========================================
# 6. 📅 캘린더 뷰 (수정사항 1 반영: 근무/근태 캘린더 시인성 보정)
# ==========================================
st.markdown("---")
st.subheader(f"📅 [{target_user}] 님 {year}년 {month}월 캘린더")

cal_mode = st.selectbox(
    "🔄 캘린더 모드 선택",
    ["1️⃣ 근무 / 근태 확인 캘린더 (출퇴근·근무시간·지각/조퇴)", "2️⃣ 사내 일정 확인 캘린더 (미팅·회의실·업무스케줄)"]
)

first_weekday, _ = calendar.monthrange(year, month)

if "1️⃣" in cal_mode:
    st.info(f"💡 **[{target_user}]** 님의 출퇴근 및 근무시간 / 잔업시간 캘린더입니다.")
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

                # [수정 1] 배경색 대비를 명확히 하여 글자가 또렷하게 보이도록 CSS 보정
                if att_day and att_day.get("clock_in") and att_day.get("clock_in") != "-":
                    w_h, o_h, l_m, e_m, b_h, t_w_h = calculate_work_and_overtime(
                        att_day.get("clock_in"), att_day.get("clock_out"),
                        att_day.get("break_hours"), att_day.get("late_mins"), att_day.get("early_mins")
                    )
                    
                    line1 = f"⏰ {att_day.get('clock_in','-')} ~ {att_day.get('clock_out','-')}"
                    line2 = f"⏱️ 근무: {t_w_h:.2f}h"
                    line3 = f"(잔업 {o_h:.2f}h)"
                    
                    extra_status = ""
                    if l_m > 0:
                        extra_status += f"<br><span style='color: #C53030; font-weight: bold;'>⚠️ 지각 {l_m}분</span>"
                    if e_m > 0:
                        extra_status += f"<br><span style='color: #DD6B20; font-weight: bold;'>⚠️ 조퇴 {e_m}분</span>"
                    if att_day.get("status") and att_day.get("status") != "정상근무":
                        extra_status += f"<br><span style='color: #2B6CB0; font-weight: bold;'>🏷️ {att_day.get('status')}</span>"

                    card_html = f"""
                    <div style="background-color: #EBF5FF; color: #1A202C; padding: 8px; border-radius: 6px; border: 1px solid #BEE3F8; margin-bottom: 5px; font-size: 0.88rem; line-height: 1.4;">
                        <b style="color: #2D3748; font-size: 0.95rem;">{day_counter}일</b><br>
                        <span style="color: #2B6CB0; font-weight: 600;">{line1}</span><br>
                        <span style="color: #1A202C;">{line2}</span><br>
                        <span style="color: #4A5568;">{line3}</span>
                        {extra_status}
                    </div>
                    """
                else:
                    card_html = f"""
                    <div style="background-color: #F7FAFC; color: #A0AEC0; padding: 8px; border-radius: 6px; border: 1px solid #E2E8F0; margin-bottom: 5px; font-size: 0.88rem;">
                        <b style="color: #718096;">{day_counter}일</b><br>
                        ─
                    </div>
                    """

                grid_cols[idx].markdown(card_html, unsafe_allow_html=True)
                day_counter += 1

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
# 7. 📋 타임카드 테이블 (수정사항 2 반영: 주말/공휴일 색상 강조 및 기본 휴무일 상태)
# ==========================================
st.markdown("---")
st.subheader(f"📋 [{target_user}] 님 일별 타임카드 상세 내역")
st.caption("💡 각 행 오른쪽 **[✏️ 수정]** 버튼을 눌러 출퇴근 시각 및 지각/조퇴 상태를 직접 수정할 수 있습니다.")

h_col1, h_col2, h_col3, h_col4, h_col5, h_col6, h_col7, h_col8, h_col9, h_col10, h_col11, h_col12 = st.columns([1.2, 1, 1, 1, 1, 1.2, 0.8, 0.8, 0.8, 1, 1.5, 0.8])
h_col1.markdown("**날짜**")
h_col2.markdown("**출근**")
h_col3.markdown("**퇴근**")
h_col4.markdown("**근무**")
h_col5.markdown("**잔업**")
h_col6.markdown("**총 근무시간**")
h_col7.markdown("**지각**")
h_col8.markdown("**조퇴**")
h_col9.markdown("**휴식**")
h_col10.markdown("**상태**")
h_col11.markdown("**비고**")
h_col12.markdown("**수정**")
st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

for d in range(1, last_day + 1):
    curr_date = datetime.date(year, month, d)
    date_str = curr_date.strftime("%Y-%m-%d")
    weekday_num = curr_date.weekday() # 0:월 ~ 5:토, 6:일
    
    # [수정 2] 토요일, 일요일, 일본 공휴일 연동 판단 로직
    is_saturday = (weekday_num == 5)
    is_sunday = (weekday_num == 6)
    is_japan_holiday = (date_str in JAPAN_HOLIDAYS)
    is_off_day = is_saturday or is_sunday or is_japan_holiday

    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == target_user), None)

    # [수정 2] 주말/공휴일 기본 상태를 '휴무일'로 설정 (출퇴근 기록이 없는 경우)
    if is_off_day and (not att or not att.get("clock_in") or att.get("clock_in") == "-"):
        c_in = "-"
        c_out = "-"
        stat = "휴무일"
        note = ""
        w_hrs, o_hrs, l_mins, e_mins, b_hrs, tot_w_hrs = 0.0, 0.0, 0, 0, 0.0, 0.0
    else:
        c_in = att.get("clock_in", "-") if att else "-"
        c_out = att.get("clock_out", "-") if att else "-"
        m_break = att.get("break_hours") if att else None
        m_late = att.get("late_mins") if att else None
        m_early = att.get("early_mins") if att else None
        
        # 주말/공휴일 기록이 기본 '미기록'인 경우에도 '휴무일'로 우선 표시
        default_stat_val = "휴무일" if is_off_day else "미기록"
        stat = att.get("status", default_stat_val) if att else default_stat_val
        note = att.get("note", "") if att else ""

        w_hrs, o_hrs, l_mins, e_mins, b_hrs, tot_w_hrs = calculate_work_and_overtime(c_in, c_out, m_break, m_late, m_early)

    # [수정 2] 토요일(파란계열), 일요일/공휴일(붉은계열) 가시성 스타일 적용
    date_label = f"{month}/{d}({weekdays_kr[weekday_num]})"
    if is_saturday:
        date_disp = f"<span style='color: #1D4ED8; font-weight: bold; background-color: #EFF6FF; padding: 2px 6px; border-radius: 4px;'>{date_label}</span>"
    elif is_sunday or is_japan_holiday:
        holiday_tag = " (공휴일)" if is_japan_holiday and not is_sunday else ""
        date_disp = f"<span style='color: #DC2626; font-weight: bold; background-color: #FEF2F2; padding: 2px 6px; border-radius: 4px;'>{date_label}{holiday_tag}</span>"
    else:
        date_disp = date_label

    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12 = st.columns([1.2, 1, 1, 1, 1, 1.2, 0.8, 0.8, 0.8, 1, 1.5, 0.8])
    
    c1.markdown(date_disp, unsafe_allow_html=True)
    c2.write(c_in)
    c3.write(c_out)
    c4.write(f"**{w_hrs:.2f}**")
    c5.write(f"**{o_hrs:.2f}**")
    c6.write(f"**{tot_w_hrs:.2f}**")
    c7.write(str(l_mins))
    c8.write(str(e_mins))
    c9.write(f"{b_hrs:.2f}")
    
    # 상태 열 텍스트 스타일링 (휴무일 강조)
    if stat == "휴무일":
        c10.markdown(f"<span style='color: #718096; font-weight: bold;'>{stat}</span>", unsafe_allow_html=True)
    else:
        c10.write(stat)
        
    c11.write(note)

    if c12.button("✏️", key=f"btn_edit_{date_str}"):
        if st.session_state.editing_date == date_str:
            st.session_state.editing_date = None
        else:
            st.session_state.editing_date = date_str
        st.rerun()

    if st.session_state.editing_date == date_str:
        with st.container():
            st.info(f"🛠️ **[{month}/{d}({weekdays_kr[weekday_num]})] 타임카드 직접 수정 (지각/조퇴 입력 지원)**")
            with st.form(f"inline_edit_form_{date_str}"):
                ec1, ec2, ec3, ec4, ec5, ec6, ec7 = st.columns([1.5, 1.5, 1, 1, 1, 1.5, 2])
                edit_in = ec1.text_input("출근시간", value=(c_in if c_in != "-" else "09:00"))
                edit_out = ec2.text_input("퇴근시간", value=(c_out if c_out != "-" else "18:00"))
                edit_break = ec3.number_input("휴식", value=b_hrs, step=0.5)
                edit_late = ec4.number_input("지각", value=l_mins, step=1)
                edit_early = ec5.number_input("조퇴", value=e_mins, step=1)
                
                status_opts = ["정상근무", "지각", "조퇴", "연장근무", "연차/휴가", "반차", "결근", "휴무일"]
                s_idx = status_opts.index(stat) if stat in status_opts else 0
                edit_status = ec6.selectbox("상태", status_opts, index=s_idx)
                edit_note = ec7.text_input("비고", value=note)

                sub1, sub2 = st.columns([1, 4])
                if sub1.form_submit_button("💾 수정 저장", type="primary"):
                    if att:
                        att.update({
                            "clock_in": edit_in, "clock_out": edit_out,
                            "break_hours": edit_break, "late_mins": edit_late, "early_mins": edit_early,
                            "status": edit_status, "note": edit_note
                        })
                    else:
                        st.session_state.attendance_logs.append({
                            "user_name": target_user, "date": date_str,
                            "clock_in": edit_in, "clock_out": edit_out,
                            "break_hours": edit_break, "late_mins": edit_late, "early_mins": edit_early,
                            "status": edit_status, "note": edit_note
                        })
                    st.session_state.editing_date = None
                    st.success(f"[{month}/{d}({weekdays_kr[weekday_num]})] 데이터가 수정 저장되었습니다.")
                    st.rerun()

# CSV 내보내기
export_list = []
for d in range(1, last_day + 1):
    curr_date = datetime.date(year, month, d)
    date_str = curr_date.strftime("%Y-%m-%d")
    weekday_num = curr_date.weekday()
    is_off_day = (weekday_num in [5, 6]) or (date_str in JAPAN_HOLIDAYS)
    
    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == target_user), None)
    c_in = att.get("clock_in", "-") if att else "-"
    c_out = att.get("clock_out", "-") if att else "-"
    m_break = att.get("break_hours") if att else None
    m_late = att.get("late_mins") if att else None
    m_early = att.get("early_mins") if att else None
    
    default_stat_val = "휴무일" if is_off_day else "미기록"
    
    w_hrs, o_hrs, l_mins, e_mins, b_hrs, tot_w_hrs = calculate_work_and_overtime(c_in, c_out, m_break, m_late, m_early)
    export_list.append({
        "날짜": date_str, "출근시간": c_in, "퇴근시간": c_out,
        "근무시간": w_hrs, "잔업시간": o_hrs, "총근무시간": tot_w_hrs,
        "지각": l_mins, "조퇴": e_mins, "휴식시간": b_hrs,
        "상태": att.get("status", default_stat_val) if att else default_stat_val,
        "비고": att.get("note", "") if att else ""
    })

csv_data = pd.DataFrame(export_list).to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 타임카드 CSV 내보내기",
    data=csv_data,
    file_name=f"{target_user}_타임카드_{year}_{month}.csv",
    mime="text/csv"
)

# ==========================================
# 8. 📑 휴가/근태 신청 이력 및 결재 승인
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
    st.caption("신청 내역이 없습니다.")

if is_admin:
    pending_reqs = [r for r in st.session_state.schedule_requests if r["status"] in ["대기중", "승인대기"]]
    if pending_reqs:
        st.markdown("##### ⚡ 관리자 결재 대기 건 승인/반려")
        for p_req in pending_reqs:
            col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
            col_p1.write(f"📌 **[{p_req['user_name']}]** {p_req['date']} - {p_req['type']} ({p_req['reason']})")
            if col_p2.button("✅ 승인", key=f"app_ok_{p_req['id']}"):
                p_req["status"] = "승인완료"
                if "연차" in p_req["type"]:
                    st.session_state.user_vacation_info[p_req['user_name']]["used"] += 1.0
                elif "반차" in p_req["type"]:
                    st.session_state.user_vacation_info[p_req['user_name']]["used"] += 0.5
                st.success("승인되었습니다.")
                st.rerun()
            if col_p3.button("❌ 반려", key=f"app_no_{p_req['id']}"):
                p_req["status"] = "반려"
                st.warning("반려되었습니다.")
                st.rerun()
