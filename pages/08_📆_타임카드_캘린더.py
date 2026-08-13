import streamlit as st

st.set_page_config(page_title="타임카드 캘린더", layout="wide")

import calendar
import datetime
import io
import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()
user = st.session_state.get("logged_in_user")

st.title("📅 타임카드 관리 및 스케줄 캘린더")
st.markdown("---")

# ==========================================
# 1. 세션 상태 초기화 및 사용자 권한 확인
# ==========================================
if "tc_year" not in st.session_state:
    st.session_state.tc_year = 2026
if "tc_month" not in st.session_state:
    st.session_state.tc_month = 8

if "schedule_requests" not in st.session_state:
    st.session_state.schedule_requests = []

if "attendance_logs" not in st.session_state:
    st.session_state.attendance_logs = [
        {"user_name": "관리자", "date": "2026-08-03", "clock_in": "08:50", "clock_out": "18:30"},
        {"user_name": "관리자", "date": "2026-08-04", "clock_in": "09:05", "clock_out": "18:00"},
        {"user_name": "김사원", "date": "2026-08-03", "clock_in": "09:00", "clock_out": "18:00"},
        {"user_name": "이대리", "date": "2026-08-04", "clock_in": "08:45", "clock_out": "19:15"},
    ]

# 로그인 유저 정보 및 권한 체크
logged_user_name = user["name"] if user else "관리자"
is_admin = user.get("role") == "admin" if user else True  # 관리자 여부 확인

# 등록된 전체 직원 목록 추출
all_users = st.session_state.get("users", [])
user_list = [u["name"] for u in all_users] if all_users else ["관리자", "김사원", "이대리"]
if logged_user_name not in user_list:
    user_list.append(logged_user_name)

# 관리자일 경우 선택된 대상 직원, 일반 직원은 본인 고정
if is_admin:
    col_adm1, col_adm2 = st.columns([2, 3])
    with col_adm1:
        selected_target_user = st.selectbox("👤 조회/관리할 직원 선택 (관리자 전용)", user_list, index=0)
    with col_adm2:
        st.info(f"🔑 관리자 권한 접속: **[{selected_target_user}]** 님의 타임카드를 조회 및 관리 중입니다.")
else:
    selected_target_user = logged_user_name
    st.caption(f"👤 **[{selected_target_user}]** 님의 타임카드 화면입니다.")

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
# 2. 타임카드 정밀 연산 로직
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
# 3. 월 선택 네비게이션
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
# 4. 상단 작업 버튼 (스케줄 신청 / 엑셀 출력)
# ==========================================
col_btn1, col_btn2 = st.columns([1, 1])

# --- [스케줄 신청 버튼] ---
with col_btn1:
    with st.popover("📝 스케줄 신청 (휴가/시간변경)", use_container_width=True):
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
                st.session_state.schedule_requests.append({
                    "user_name": selected_target_user,
                    "date": str(req_date),
                    "type": req_type,
                    "start_time": req_start.strftime("%H:%M") if "시간" in req_type else "-",
                    "end_time": req_end.strftime("%H:%M") if "시간" in req_type else "-",
                    "reason": req_reason,
                    "status": "승인대기"
                })
                st.success(f"[{selected_target_user}] 님의 스케줄 변경 신청이 접수되었습니다.")
                st.rerun()

# 대상 직원의 일별 데이터 연산
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
        "신청": req_status,
        "날짜": date_disp,
        "출근시간": in_time,
        "퇴근시간": out_time,
        "근무": f"{w:.2f}",
        "잔업": f"{ot:.2f}",
        "지각": f"{td:.2f}",
        "조퇴": f"{el:.2f}",
        "휴식": f"{br:.2f}",
        "노동합계": f"{total:.2f}"
    })

df_daily = pd.DataFrame(daily_rows)

# --- [출력 버튼 (엑셀 다운로드)] ---
with col_btn2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_daily.to_excel(writer, index=False, sheet_name=f"{month}월_타임카드_상세")
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
        label=f"🖨️ [{selected_target_user}] {month}월 타임카드 엑셀 출력 (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"Timecard_{year}_{month:02d}_{selected_target_user}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. 캘린더 화면 (대형 표시)
# ==========================================
st.subheader(f"📅 [{selected_target_user}] 님의 캘린더")

cal_obj = calendar.Calendar(firstweekday=6)
month_weeks = cal_obj.monthdayscalendar(year, month)

cols_hdr = st.columns(7)
day_headers = ["일", "월", "화", "수", "목", "금", "토"]
for idx, dh in enumerate(day_headers):
    color = "red" if idx == 0 else ("blue" if idx == 6 else "inherit")
    cols_hdr[idx].markdown(f"<h4 style='text-align: center; color: {color}; margin-bottom:4px;'>{dh}</h4>", unsafe_allow_html=True)

st.markdown("---")

for week in month_weeks:
    cols_w = st.columns(7)
    for idx, day_num in enumerate(week):
        with cols_w[idx]:
            if day_num == 0:
                st.markdown("<div style='background-color:#f8f9fa; height:100px; border-radius:4px; border:1px solid #eee;'></div>", unsafe_allow_html=True)
            else:
                date_str = f"{year}-{month:02d}-{day_num:02d}"
                att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == selected_target_user), None)
                req = next((r for r in st.session_state.schedule_requests if r["date"] == date_str and r["user_name"] == selected_target_user), None)

                color = "red" if idx == 0 else ("blue" if idx == 6 else "#333")
                card_html = f"<div style='border:1px solid #ddd; border-radius:6px; padding:6px; height:105px; background-color:#fff; overflow:hidden;'>"
                card_html += f"<span style='font-weight:bold; font-size:13px; color:{color};'>{month}/{day_num}</span>"

                if att:
                    card_html += f"<div style='font-size:11px; color:#28a745; margin-top:2px;'><b>출:</b> {att['clock_in']} / <b>퇴:</b> {att['clock_out']}</div>"
                if req:
                    card_html += f"<div style='font-size:10px; background-color:#fff3cd; padding:1px 3px; border-radius:2px; margin-top:2px;'>[{req['type']}] {req['status']}</div>"

                card_html += "</div>"
                st.markdown(card_html, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# 6. 월별 데이터 시간집계
# ==========================================
st.subheader(f"📊 [{selected_target_user}] 님 월별 데이터 시간집계")

m1, m2, m3, m4 = st.columns(4)
m1.metric("근무 시간 (총합)", f"{tot_work:.2f} 시간")
m2.metric("잔업 시간 (18시 이후)", f"{tot_ot:.2f} 시간")
m3.metric("지각 / 조퇴 (시간)", f"{tot_tard:.2f} / {tot_early:.2f}")
m4.metric("노동 합계 (근무+잔업)", f"{tot_sum:.2f} 시간")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 7. 일별 상세 타임카드
# ==========================================
st.subheader(f"📋 일별 상세 타임카드 ({month}월 1일 ~ {last_day}일)")
st.dataframe(df_daily, use_container_width=True, height=400)

# ==========================================
# 8. [관리자 전용] 타임카드 직접 수정 및 삭제
# ==========================================
if is_admin:
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.subheader(f"🛠️ [{selected_target_user}] 님의 타임카드 관리자 직접 수정/삭제")

    with st.expander("✏️ 특정 일자 출퇴근 시간 수정 / 입력 / 삭제"):
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            edit_date = st.date_input("수정 대상 날짜", datetime.date(year, month, 1))
        with col_m2:
            edit_in = st.text_input("출근 시간 (HH:MM)", value="09:00")
        with col_m3:
            edit_out = st.text_input("퇴근 시간 (HH:MM)", value="18:00")
        with col_m4:
            st.write(" ")
            st.write(" ")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 저장", type="primary"):
                    date_key = str(edit_date)
                    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_key and a.get("user_name") == selected_target_user), None)
                    if att:
                        att["clock_in"] = edit_in
                        att["clock_out"] = edit_out
                    else:
                        st.session_state.attendance_logs.append({
                            "user_name": selected_target_user,
                            "date": date_key,
                            "clock_in": edit_in,
                            "clock_out": edit_out
                        })
                    st.success(f"{date_key} 기록이 성공적으로 업데이트되었습니다.")
                    st.rerun()
            with col_b2:
                if st.button("🗑️ 삭제"):
                    date_key = str(edit_date)
                    st.session_state.attendance_logs = [
                        a for a in st.session_state.attendance_logs 
                        if not (a["date"] == date_key and a.get("user_name") == selected_target_user)
                    ]
                    st.success(f"{date_key} 기록이 삭제되었습니다.")
                    st.rerun()
