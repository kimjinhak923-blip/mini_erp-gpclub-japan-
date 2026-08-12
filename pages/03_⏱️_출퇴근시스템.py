import datetime
import pytz
import pandas as pd
import streamlit as st

st.set_page_config(page_title="출퇴근시스템", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

user = st.session_state.logged_in_user
is_visitor = user.get("role") == "방문자"

def get_tokyo_time():
    return datetime.datetime.now(pytz.timezone("Asia/Tokyo"))

def calculate_work_hours(clock_in_str, clock_out_time):
    if not clock_out_time:
        return "근무 중"
    start_minutes = 9 * 60
    out_minutes = clock_out_time.hour * 60 + clock_out_time.minute
    if out_minutes <= start_minutes:
        return "0시간 0분"
    total_minutes = out_minutes - start_minutes
    if out_minutes >= 13 * 60:
        total_minutes -= 60
    elif out_minutes > 12 * 60:
        total_minutes -= out_minutes - 12 * 60
    return f"{max(0, total_minutes) // 60}시간 {max(0, total_minutes) % 60}분"

st.header("⏱️ 출퇴근 관리 시스템")
tokyo_now = get_tokyo_time()
today_str = tokyo_now.strftime("%Y-%m-%d")

record = next((r for r in st.session_state.attendance_records if r["userId"] == user["id"] and r["date"] == today_str), None)

c1, c2 = st.columns(2)
with c1:
    st.subheader("☀️ 오늘 나의 출퇴근")
    st.write(f"- 오늘 날짜: {today_str}")
    st.write(f"- 출근 시각: {record['clockIn'] if record else '--:--:--'}")
    st.write(f"- 퇴근 시각: {record['clockOut'] if record else '--:--:--'}")
    st.write(f"- 실근무시간: {record['calculatedHoursStr'] if record else '0시간 0분'}")

    b1, b2 = st.columns(2)
    if b1.button("☀️ 출근", use_container_width=True, disabled=is_visitor):
        if record and record["clockIn"]:
            st.warning("이미 출근 처리되었습니다.")
        else:
            st.session_state.attendance_records.append({
                "date": today_str,
                "userId": user["id"],
                "userName": user["name"],
                "clockIn": tokyo_now.strftime("%H:%M:%S"),
                "clockOut": "--:--:--",
                "calculatedHoursStr": "근무 중",
            })
            st.success("출근 완료")
            st.rerun()

    if b2.button("🌙 퇴근", use_container_width=True, disabled=is_visitor):
        if not record or not record["clockIn"]:
            st.error("출근 기록이 없습니다.")
        else:
            record["clockOut"] = tokyo_now.strftime("%H:%M:%S")
            record["calculatedHoursStr"] = calculate_work_hours(record["clockIn"], tokyo_now.time())
            st.success("퇴근 완료")
            st.rerun()

with c2:
    st.subheader("📋 전체 출퇴근 기록")
    if st.session_state.attendance_records:
        st.dataframe(pd.DataFrame(st.session_state.attendance_records), use_container_width=True)
