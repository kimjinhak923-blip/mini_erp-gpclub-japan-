import datetime
import pytz
import pandas as pd
import streamlit as st

user = st.session_state.get("logged_in_user")

st.title("⏰ 근태 및 출퇴근 관리")
st.markdown("---")

if not user:
    st.warning("로그인이 필요한 페이지입니다. 메인 페이지에서 먼저 로그인해 주세요.")
else:
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    now = datetime.datetime.now(tokyo_tz)
    today_str = now.strftime("%Y-%m-%d")
    now_time_str = now.strftime("%H:%M:%S")

    st.subheader(f"📅 오늘 날짜: {today_str} (도쿄 기준)")
    st.write(f"**현재 시간:** {now_time_str}")

    my_records = [
        r
        for r in st.session_state.attendance_records
        if r["user_id"] == user["id"] and r["date"] == today_str
    ]
    today_record = my_records[0] if my_records else None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔔 출근 등록", use_container_width=True):
            if today_record:
                st.warning("이미 오늘 출근 기록이 존재합니다.")
            else:
                new_rec = {
                    "user_id": user["id"],
                    "name": user["name"],
                    "date": today_str,
                    "check_in": now_time_str,
                    "check_out": None,
                    "work_hours": 0.0,
                }
                st.session_state.attendance_records.append(new_rec)
                st.success(f"{now_time_str} 출근 등록 완료!")
                st.rerun()

    with col2:
        if st.button("🔕 퇴근 등록", use_container_width=True):
            if not today_record:
                st.error("출근 기록이 없습니다. 먼저 출근 등록을 해주세요.")
            elif today_record["check_out"] is not None:
                st.warning("이미 퇴근 등록이 완료되었습니다.")
            else:
                today_record["check_out"] = now_time_str
                t_in = datetime.datetime.strptime(today_record["check_in"], "%H:%M:%S")
                t_out = datetime.datetime.strptime(now_time_str, "%H:%M:%S")
                diff_hours = (t_out - t_in).total_seconds() / 3600.0

                if t_in.hour <= 12 and t_out.hour >= 13:
                    diff_hours = max(0.0, diff_hours - 1.0)

                today_record["work_hours"] = round(diff_hours, 2)
                st.success(f"{now_time_str} 퇴근 등록 완료! (근무시간: {today_record['work_hours']}시간)")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 내 출퇴근 이력")
    user_atts = [
        r for r in st.session_state.attendance_records if r["user_id"] == user["id"]
    ]
    if user_atts:
        st.dataframe(pd.DataFrame(user_atts), use_container_width=True)
    else:
        st.info("출퇴근 기록이 존재하지 않습니다.")
