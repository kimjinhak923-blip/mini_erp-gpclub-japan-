import streamlit as st
from datetime import datetime, time, timedelta
import pandas as pd
from utils.supabase_client import supabase

def render():
    st.header("⏰ 출퇴근 관리")
    user = st.session_state["user"]
    today = datetime.now().date()
    now_time = datetime.now().time()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ 출근하기", use_container_width=True):
            # 출근 시간이 8:50이어도 계산용 시작시간은 09:00으로 고정
            supabase.table("attendance").upsert({
                "user_id": user["id"],
                "work_date": str(today),
                "clock_in": now_time.strftime("%H:%M:%S"),
                "work_start_calc": "09:00:00"
            }, on_conflict="user_id, work_date").execute()
            st.success(f"출근 등록 완료 ({now_time.strftime('%H:%M:%S')}) - 근무계산 기준: 09:00")
            st.rerun()
            
    with col2:
        if st.button("🌙 퇴근하기", use_container_width=True):
            # 잔업시간 계산 (18:00 이후 근무 분을 0.00 시간 단위로 계산)
            standard_end = datetime.combine(today, time(18, 0, 0))
            current_dt = datetime.now()
            
            overtime = 0.00
            if current_dt > standard_end:
                diff_minutes = (current_dt - standard_end).total_seconds() / 60
                overtime = round(diff_minutes / 60, 2)
                
            supabase.table("attendance").update({
                "clock_out": now_time.strftime("%H:%M:%S"),
                "overtime_hours": overtime
            }).eq("user_id", user["id"]).eq("work_date", str(today)).execute()
            st.success(f"퇴근 등록 완료 ({now_time.strftime('%H:%M:%S')}) - 잔업: {overtime:.2f}시간")
            st.rerun()

    st.markdown("---")
    st.subheader("📊 근태 기록 및 엑셀 다운로드")
    
    # 조회 및 엑셀 출력
    res = supabase.table("attendance").select("work_date, clock_in, clock_out, work_start_calc, overtime_hours, user_profiles(full_name)").execute()
    if res.data:
        rows = []
        for r in res.data:
            rows.append({
                "이름": r["user_profiles"]["full_name"] if r.get("user_profiles") else "-",
                "근무일자": r["work_date"],
                "실제출근": r["clock_in"],
                "계산출근": r["work_start_calc"],
                "퇴근시간": r["clock_out"],
                "잔업시간(시간)": float(r["overtime_hours"] or 0.0)
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        
        # 엑셀 다운로드 버튼
        excel_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 근태 기록 CSV/엑셀 다운로드",
            data=excel_data,
            file_name=f"attendance_report_{today}.csv",
            mime="text/csv"
        )
