import streamlit as st

st.set_page_config(page_title="타임카드 및 캘린더", layout="wide")

import calendar
import datetime
import io
import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()
user = st.session_state.get("logged_in_user")

st.title("📅 타임카드 관리 및 스케줄/사내 캘린더")
st.markdown("---")

# ==========================================
# 1. 세션 상태 초기화
# ==========================================
if "tc_year" not in st.session_state:
    st.session_state.tc_year = 2026
if "tc_month" not in st.session_state:
    st.session_state.tc_month = 8

# 연차 현황 데이터 초기화 (기본 부여 15일)
if "user_vacation_info" not in st.session_state:
    st.session_state.user_vacation_info = {
        "관리자": {"granted": 15.0, "used": 2.0},
        "김사원": {"granted": 15.0, "used": 1.0},
        "이대리": {"granted": 15.0, "used": 0.0},
    }

# 스케줄 / 휴가 신청 데이터
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
        }
    ]

# 출퇴근 기록 데이터
if "attendance_logs" not in st.session_state:
    st.session_state.attendance_logs = [
        {"user_name": "관리자", "date": "2026-08-03", "clock_in": "08:50", "clock_out": "18:30"},
        {"user_name": "관리자", "date": "2026-08-04", "clock_in": "09:05", "clock_out": "18:00"},
        {"user_name": "김사원", "date": "2026-08-03", "clock_in": "09:00", "clock_out": "18:00"},
        {"user_name": "이대리", "date": "2026-08-04", "clock_in": "08:45", "clock_out": "19:15"},
    ]

# 회사 재량 휴무일 데이터
if "company_holidays" not in st.session_state:
    st.session_state.company_holidays = [
        {"date": "2026-08-14", "name": "회사 창립기념일 휴무", "type": "공휴일표기"},
        {"date": "2026-08-17", "name": "하계 특별 휴무", "type": "평일표기"},
    ]

# 사내 공유 일정 (외부미팅, 회의실 사용 등)
if "company_schedules" not in st.session_state:
    st.session_state.company_schedules = [
        {"id": 1, "creator": "김사원", "date": "2026-08-05", "time": "14:00~15:30", "title": "A상사 외부 미팅", "category": "외부미팅"},
        {"id": 2, "creator": "이대리", "date": "2026-08-12", "time": "10:00~11:00", "title": "대회의실 신제품 회의", "category": "회의실사용"},
    ]

# 일본 공휴일 데이터 (2026년 기준)
JAPAN_HOLIDAYS_2026 = {
    "2026-01-01": "신정 (元日)",
    "2026-01-12": "성인의 날 (成人の日)",
    "2026-02-11": "건국기념의 날 (建国記念の日)",
    "2026-02-23": "일왕 탄생일 (天皇誕生日)",
    "2026-03-20": "춘분의 날 (春分の日)",
    "2026-04-29": "쇼와의 날 (昭和の日)",
    "2026-05-03": "헌법기념일 (憲法記念日)",
    "2026-05-04": "녹색의 날 (みどもの日)",
    "2026-05-05": "어린이의 날 (こどもの日)",
    "2026-07-20": "바다의 날 (海の日)",
    "2026-08-11": "산의 날 (山の日)",
    "2026-09-21": "경로의 날 (敬老の日)",
    "2026-09-22": "국민의 휴일 (国民の休日)",
    "2026-09-23": "추분의 날 (秋分の日)",
    "2026-10-12": "체육의 날 (スポーツの日)",
    "2026-11-03": "문화의 날 (文化の日)",
    "2026-11-23": "근로감사의 날 (勤労感謝の日)",
}


# ==========================================
# 2. 사용자 권한 및 관리자 드롭다운 설정
# ==========================================
logged_user_name = user["name"] if user else "관리자"
is_admin = (user.get("role") == "admin") if user else True

# 등록된 직원 목록
all_users = st.session_state.get("users", [])
user_list = [u["name"] for u in all_users] if all_users else ["관리자", "김사원", "이대리"]
for u_name in ["관리자", "김사원", "이대리"]:
    if u_name not in user_list:
        user_list.append(u_name)

# 관리자인 경우 상단 드롭다운 배치, 일반 직원은 본인 고정
if is_admin:
    col_adm1, col_adm2 = st.columns([2, 3])
    with col_adm1:
        selected_target_user = st.selectbox("👤 [관리자] 조회 및 관리 대상 직원 선택", user_list, index=0)
    with col_adm2:
        st.info(f"🔑 관리자 권한 로그인: 현재 **[{selected_target_user}]** 님의 타임카드/휴가를 관리 중입니다.")
else:
    selected_target_user = logged_user_name
    st.caption(f"👤 **[{selected_target_user}]** 님의 타임카드 화면입니다.")

# 휴가 정보 보장
if selected_target_user not in st.session_state.user_vacation_info:
    st.session_state.user_vacation_info[selected_target_user] = {"granted": 15.0, "used": 0.0}

v_info = st.session_state.user_vacation_info[selected_target_user]
rem_vacation = v_info["granted"] - v_info["used"]

# 상단 연차 현황 요약
st.markdown(
    f"💡 **[{selected_target_user}] 님의 연차 현황:** 부여 연차 `{v_info['granted']}일` | 사용 연차 `{v_info['used']}일` | **잔여 연차 `{rem_vacation}일`**"
)

year = st.session_state.tc_year
month = st.session_state.tc_month
weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]

_, last_day = calendar.monthrange(year, month)
start_date = datetime.date(year, month, 1)
end_date = datetime.date(year, month, last_day)

start_str = f"{start_date.strftime('%Y/%m/%d')}({weekdays_kr[start_date.weekday()]})"
end_str = f"{end_date.strftime('%Y/%m/%d')}({weekdays_kr[end_date.weekday()]})"
period_display = f"{start_str} ~ {end_str}"


# ==========================================
# 3. 타임카드 연산 로직 함수
# ==========================================
def calculate_daily_timecard(clock_in_str, clock_out_str):
    if not clock_in_str or not clock_out_str or clock_in_str == "-" or clock_out_str == "-":
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    fmt = "%H:%M"
    try:
        t_in = datetime.datetime.strptime(clock_in_str, fmt)
        t_out = datetime.datetime.strptime(clock_out_str, fmt)
        std_in = datetime.datetime.strptime("09:00", fmt)
        std_out = datetime.datetime.strptime("18:00", fmt)
    except ValueError:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    tardiness = round((t_in - std_in).total_seconds() / 3600.0, 2) if t_in > std_in else 0.0
    early_leave = round((std_out - t_out).total_seconds() / 3600.0, 2) if t_out < std_out else 0.0
    overtime = round((t_out - std_out).total_seconds() / 3600.0, 2) if t_out > std_out else 0.0
    break_time = 1.00
    work_time = max(0.00, round(8.00 - tardiness - early_leave, 2))
    total_labor = round(work_time + overtime, 2)

    return work_time, overtime, tardiness, early_leave, break_time, total_labor


# ==========================================
# 4. 월 선택 네비게이션
# ==========================================
col_nav1, col_nav2, col_nav3 = st.columns([1.2, 3, 1.2])

with col_nav1:
    if st.button("◀ 지난달", use_container_width=True):
        if month == 1:
            st.session_state.tc_year -= 1
            st.session_state.tc_month = 12
        else:
            st.session_state.tc_month -= 1
        st.rerun()

with col_nav2:
    st.markdown(
        f"<h3 style='text-align: center; margin:0;'>🗓️ {year}년 {month:02d}월</h3>"
        f"<p style='text-align: center; color: #555; font-weight: bold; margin-top: 4px;'>기간: {period_display}</p>",
        unsafe_allow_html=True,
    )

with col_nav3:
    if st.button("다음달 ▶", use_container_width=True):
        if month == 12:
            st.session_state.tc_year += 1
            st.session_state.tc_month = 1
        else:
            st.session_state.tc_month += 1
        st.rerun()

st.markdown("---")


# ==========================================
# 5. 상단 작업 버튼 (스케줄 신청 / 일정 등록 / 엑셀 출력)
# ==========================================
col_btn1, col_btn2, col_btn3 = st.columns([1.2, 1.2, 1.2])

# --- [스케줄 / 휴가 신청 (사원용/관리자용)] ---
with col_btn1:
    with st.popover("📝 스케줄 / 휴가 신청", use_container_width=True):
        st.subheader("📝 스케줄 / 휴가 신청서")
        with st.form("sched_form"):
            req_date = st.date_input("신청 날짜", datetime.date(year, month, 1))
            req_type = st.selectbox("신청 구분", ["연차/휴가", "반차", "출근시간 변경", "퇴근시간 변경", "휴일 근무"])
            
            c_t1, c_t2 = st.columns(2)
            with c_t1:
                req_start = st.time_input("희망 출근시간", datetime.time(9, 0))
            with c_t2:
                req_end = st.time_input("희망 퇴근시간", datetime.time(18, 0))
                
            req_reason = st.text_area("신청 사유", placeholder="사유를 입력해 주세요.")

            if st.form_submit_button("신청 제출"):
                new_id = len(st.session_state.schedule_requests) + 1
                st.session_state.schedule_requests.append({
                    "id": new_id,
                    "user_name": selected_target_user,
                    "date": str(req_date),
                    "type": req_type,
                    "start_time": req_start.strftime("%H:%M") if "시간" in req_type else "-",
                    "end_time": req_end.strftime("%H:%M") if "시간" in req_type else "-",
                    "reason": req_reason,
                    "status": "승인대기",
                    "deducted": False,
                })
                st.success(f"[{selected_target_user}] 님의 스케줄/휴가 신청이 제출되었습니다.")
                st.rerun()

# --- [사내 공유 일정 등록 (일반직원/관리자 모두 가능)] ---
with col_btn2:
    with st.popover("📌 사내 공유 일정 등록", use_container_width=True):
        st.subheader("📌 업무/미팅/회의실 일정 공유")
        st.caption("※ 일반 직원은 외부미팅, 회의실 사용 등 업무 공유 일정만 등록 가능합니다.")
        with st.form("company_sched_form"):
            cs_date = st.date_input("일정 날짜", datetime.date(year, month, 1))
            cs_cat = st.selectbox("일정 카테고리", ["외부미팅", "회의실사용", "업무일정", "기타"])
            cs_time = st.text_input("시간 (예: 14:00~15:30)", value="10:00~11:00")
            cs_title = st.text_input("일정 내용/제목", placeholder="예: A상사 미팅 / 대회의실 사용")

            if st.form_submit_button("일정 공유 등록"):
                cs_id = len(st.session_state.company_schedules) + 1
                st.session_state.company_schedules.append({
                    "id": cs_id,
                    "creator": logged_user_name,
                    "date": str(cs_date),
                    "time": cs_time,
                    "title": cs_title,
                    "category": cs_cat
                })
                st.success("사내 공유 일정에 성공적으로 등록되었습니다.")
                st.rerun()

# --- [일별 데이터 생성 및 엑셀 다운로드] ---
daily_rows = []
tot_work, tot_ot, tot_tard, tot_early, tot_break, tot_sum = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

for d in range(1, last_day + 1):
    curr_date = datetime.date(year, month, d)
    date_str_full = curr_date.strftime("%Y-%m-%d")
    date_disp = f"{month}/{d}({weekdays_kr[curr_date.weekday()]})"

    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str_full and a.get("user_name") == selected_target_user), None)
    
    in_time = att["clock_in"] if att else "-"
    out_time = att["clock_out"] if att else "-"

    w, ot, td, el, br, total = calculate_daily_timecard(in_time, out_time)

    req = next((r for r in st.session_state.schedule_requests if r["date"] == date_str_full and r["user_name"] == selected_target_user), None)
    req_status = f"[{req['type']}] {req['status']}" if req else "일반"

    tot_work += w
    tot_ot += ot
    tot_tard += td
    tot_early += el
    tot_break += br
    tot_sum += total

    daily_rows.append({
        "날짜": date_disp,
        "raw_date": date_str_full,
        "출근시간": in_time,
        "퇴근시간": out_time,
        "근무": f"{w:.2f}",
        "잔업": f"{ot:.2f}",
        "지각": f"{td:.2f}",
        "조퇴": f"{el:.2f}",
        "휴식": f"{br:.2f}",
        "노동합계": f"{total:.2f}",
        "신청": req_status
    })

df_daily_display = pd.DataFrame(daily_rows)

with col_btn3:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df = df_daily_display.drop(columns=["raw_date"])
        export_df.to_excel(writer, index=False, sheet_name=f"{month}월_타임카드_상세")
        summary_df = pd.DataFrame([{
            "직원명": selected_target_user,
            "조회기간": period_display,
            "총 근무시간": f"{tot_work:.2f}",
            "총 잔업시간": f"{tot_ot:.2f}",
            "총 지각시간": f"{tot_tard:.2f}",
            "총 조퇴시간": f"{tot_early:.2f}",
            "총 휴식시간": f"{tot_break:.2f}",
            "총 노동합계": f"{tot_sum:.2f}",
        }])
        summary_df.to_excel(writer, index=False, sheet_name="월별_시간집계")

    st.download_button(
        label=f"🖨️ [{selected_target_user}] 엑셀 출력 (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"Timecard_{year}_{month:02d}_{selected_target_user}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 6. 관리자 전용 스케줄/휴가 승인 및 차감 처리
# ==========================================
if is_admin:
    pending_reqs = [r for r in st.session_state.schedule_requests if r["status"] == "승인대기"]
    if pending_reqs:
        with st.expander(f"⚠️ 승인 대기 중인 휴가/스케줄 신청 ({len(pending_reqs)}건)", expanded=True):
            for pr in pending_reqs:
                c1, c2, c3, c4 = st.columns([2, 3, 1, 1])
                c1.write(f"**{pr['user_name']}** ({pr['date']})")
                c2.write(f"구분: `{pr['type']}` | 사유: {pr['reason']}")
                if c3.button("✅ 승인", key=f"app_{pr['id']}"):
                    pr["status"] = "승인완료"
                    target_u = pr["user_name"]
                    if target_u not in st.session_state.user_vacation_info:
                        st.session_state.user_vacation_info[target_u] = {"granted": 15.0, "used": 0.0}
                    
                    if not pr.get("deducted", False):
                        if pr["type"] == "연차/휴가":
                            st.session_state.user_vacation_info[target_u]["used"] += 1.0
                            pr["deducted"] = True
                        elif pr["type"] == "반차":
                            st.session_state.user_vacation_info[target_u]["used"] += 0.5
                            pr["deducted"] = True

                    st.success(f"[{pr['user_name']}] 님의 신청이 승인되었으며 연차가 자동 차감 처리되었습니다.")
                    st.rerun()

                if c4.button("❌ 반려", key=f"rej_{pr['id']}"):
                    pr["status"] = "반려"
                    st.warning(f"[{pr['user_name']}] 님의 신청이 반려되었습니다.")
                    st.rerun()


# ==========================================
# 7. 캘린더 모드 선택 (개인 캘린더 vs 사내 캘린더)
# ==========================================
st.markdown("---")
col_cal_hdr, col_cal_sel = st.columns([2, 1])
with col_cal_hdr:
    st.subheader("📅 캘린더 관리")
with col_cal_sel:
    cal_mode = st.selectbox("캘린더 종류 선택", ["👤 개인 캘린더 (출퇴근)", "🏢 사내 캘린더 (휴가/공휴일/일정)"])

# 회사 재량 휴무일 추가/수정 (관리자 전용)
if is_admin and cal_mode == "🏢 사내 캘린더 (휴가/공휴일/일정)":
    with st.expander("🛠️ [관리자] 회사 재량 휴무일 추가 / 수정"):
        c_h1, c_h2, c_h3, c_h4 = st.columns([2, 2, 2, 1])
        with c_h1:
            ch_date = st.date_input("휴무일 날짜", datetime.date(year, month, 1))
        with c_h2:
            ch_name = st.text_input("휴무일 이름", value="회사 재량 휴무")
        with c_h3:
            ch_type = st.radio("표기 유형", ["공휴일표기", "평일표기"], horizontal=True)
        with c_h4:
            st.write(" ")
            st.write(" ")
            if st.button("휴무일 추가"):
                st.session_state.company_holidays.append({
                    "date": str(ch_date),
                    "name": ch_name,
                    "type": ch_type
                })
                st.success("재량 휴무일이 추가되었습니다.")
                st.rerun()

# 캘린더 그리기
cal_obj = calendar.Calendar(firstweekday=6)
month_weeks = cal_obj.monthdayscalendar(year, month)

cols_hdr = st.columns(7)
day_headers = ["일", "월", "화", "수", "목", "금", "토"]
for idx, dh in enumerate(day_headers):
    color = "#e63946" if idx == 0 else ("#1d3557" if idx == 6 else "inherit")
    cols_hdr[idx].markdown(f"<h4 style='text-align: center; color: {color}; margin-bottom:4px; font-weight:bold;'>{dh}</h4>", unsafe_allow_html=True)

st.markdown("---")

for week in month_weeks:
    cols_w = st.columns(7)
    for idx, day_num in enumerate(week):
        with cols_w[idx]:
            if day_num == 0:
                st.markdown("<div style='background-color:rgba(200,200,200,0.1); height:125px; border-radius:6px; border:1px solid #444;'></div>", unsafe_allow_html=True)
            else:
                date_str = f"{year}-{month:02d}-{day_num:02d}"
                
                # 날짜 헤더 색상 (일요일: 빨강, 토요일: 파랑, 평일: 기본)
                day_color = "#e63946" if idx == 0 else ("#2196f3" if idx == 6 else "#222222")

                jp_holiday = JAPAN_HOLIDAYS_2026.get(date_str)
                comp_holiday = next((h for h in st.session_state.company_holidays if h["date"] == date_str), None)
                
                if jp_holiday or (comp_holiday and comp_holiday["type"] == "공휴일표기"):
                    day_color = "#e63946"

                card_html = (
                    f"<div style='border:1px solid #ccc; border-radius:6px; padding:6px; height:125px; "
                    f"background-color:#ffffff; color:#111111; overflow-y:auto; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
                )
                card_html += f"<div style='font-weight:bold; font-size:14px; color:{day_color}; margin-bottom:3px;'>{month}/{day_num}</div>"

                # ------------------------------------
                # MODE 1: 개인 캘린더
                # ------------------------------------
                if cal_mode == "👤 개인 캘린더 (출퇴근)":
                    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == selected_target_user), None)
                    req = next((r for r in st.session_state.schedule_requests if r["date"] == date_str and r["user_name"] == selected_target_user), None)

                    if att:
                        card_html += f"<div style='font-size:11px; color:#1b5e20; font-weight:600; margin-top:2px;'>⏰ <b>출:</b> {att['clock_in']} / <b>퇴:</b> {att['clock_out']}</div>"
                    if req:
                        bg_c = "#d4edda" if req["status"] == "승인완료" else "#fff3cd"
                        text_c = "#155724" if req["status"] == "승인완료" else "#856404"
                        card_html += (
                            f"<div style='font-size:11px; font-weight:600; background-color:{bg_c}; color:{text_c}; "
                            f"padding:2px 4px; border-radius:3px; margin-top:3px; border:1px solid {text_c};'>"
                            f"[{req['type']}] {req['status']}</div>"
                        )

                # ------------------------------------
                # MODE 2: 사내 캘린더
                # ------------------------------------
                else:
                    # 1. 일본 공휴일
                    if jp_holiday:
                        card_html += f"<div style='font-size:11px; color:#d90429; font-weight:bold; margin-top:2px;'>🇯🇵 {jp_holiday}</div>"
                    
                    # 2. 회사 재량 휴무일
                    if comp_holiday:
                        h_color = "#d90429" if comp_holiday["type"] == "공휴일표기" else "#4a5568"
                        card_html += f"<div style='font-size:11px; color:{h_color}; font-weight:bold; margin-top:2px;'>🏢 {comp_holiday['name']}</div>"

                    # 3. 승인된 직원 휴가 (고대비 선명한 초록 뱃지)
                    approved_vacs = [r for r in st.session_state.schedule_requests if r["date"] == date_str and r["status"] == "승인완료" and ("휴가" in r["type"] or "반차" in r["type"])]
                    for av in approved_vacs:
                        card_html += (
                            f"<div style='font-size:11px; font-weight:bold; background-color:#d4edda; color:#155724; "
                            f"padding:2px 4px; border-radius:3px; margin-top:2px; border:1px solid #c3e6cb;'>"
                            f"🌴 {av['user_name']}({av['type']})</div>"
                        )

                    # 4. 사내 공유 일정 (고대비 선명한 파랑 뱃지)
                    schedules = [s for s in st.session_state.company_schedules if s["date"] == date_str]
                    for sc in schedules:
                        card_html += (
                            f"<div style='font-size:11px; font-weight:bold; background-color:#e7f3ff; color:#004085; "
                            f"padding:2px 4px; border-radius:3px; margin-top:2px; border:1px solid #b8daff;'>"
                            f"📌 {sc['creator']}: {sc['title']} ({sc['time']})</div>"
                        )

                card_html += "</div>"
                st.markdown(card_html, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)


# ==========================================
# 8. 월별 데이터 시간집계
# ==========================================
st.subheader(f"📊 [{selected_target_user}] 님 월별 데이터 시간집계")

m1, m2, m3, m4 = st.columns(4)
m1.metric("근무 시간 (총합)", f"{tot_work:.2f} 시간")
m2.metric("잔업 시간 (18시 이후 1분단위)", f"{tot_ot:.2f} 시간")
m3.metric("지각 / 조퇴 (시간)", f"{tot_tard:.2f} / {tot_early:.2f}")
m4.metric("노동 합계 (근무+잔업)", f"{tot_sum:.2f} 시간")

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 9. 일별 상세 타임카드 (관리자 셀 수정 가능 / 더블클릭)
# ==========================================
st.subheader(f"📋 일별 상세 타임카드 ({month}월 1일 ~ {last_day}일)")

if is_admin:
    st.info("💡 **[관리자 기능]** 아래 표에서 출근시간 / 퇴근시간 셀을 **더블클릭**하여 직접 수정하신 후, 하단의 **[💾 출퇴근 수정사항 저장]** 버튼을 누르면 즉시 반영 및 재계산됩니다.")
    
    edited_df = st.data_editor(
        df_daily_display[["날짜", "출근시간", "퇴근시간", "근무", "잔업", "지각", "조퇴", "휴식", "노동합계", "신청"]],
        disabled=["날짜", "근무", "잔업", "지각", "조퇴", "휴식", "노동합계", "신청"],
        use_container_width=True,
        height=400,
        key="admin_timecard_editor"
    )

    if st.button("💾 출퇴근 수정사항 저장", type="primary"):
        for idx, row in edited_df.iterrows():
            raw_d = df_daily_display.loc[idx, "raw_date"]
            new_in = str(row["출근시간"]).strip()
            new_out = str(row["퇴근시간"]).strip()

            att = next((a for a in st.session_state.attendance_logs if a["date"] == raw_d and a.get("user_name") == selected_target_user), None)
            
            if att:
                att["clock_in"] = new_in
                att["clock_out"] = new_out
            else:
                if new_in != "-" or new_out != "-":
                    st.session_state.attendance_logs.append({
                        "user_name": selected_target_user,
                        "date": raw_d,
                        "clock_in": new_in,
                        "clock_out": new_out
                    })

        st.success("타임카드 출퇴근 수정사항이 성공적으로 저장되었습니다.")
        st.rerun()

else:
    st.dataframe(
        df_daily_display[["날짜", "출근시간", "퇴근시간", "근무", "잔업", "지각", "조퇴", "휴식", "노동합계", "신청"]],
        use_container_width=True,
        height=400
    )
