import streamlit as st
from datetime import datetime
from utils.supabase_client import supabase

def render():
    st.header("📅 일정 및 휴무/연차 관리")
    user = st.session_state["user"]
    is_admin = user["role"] == "ADMIN"
    
    tab1, tab2 = st.tabs(["캘린더 및 일정", "휴무 신청 및 승인"])
    
    with tab1:
        st.subheader("월간 일정표")
        # 등록 폼 (권한 제어)
        with st.expander("➕ 일정 등록"):
            with st.form("add_schedule_form"):
                title = st.text_input("일정 제목")
                s_date = st.date_input("일자")
                
                # 권한별 구분 제한
                available_categories = ["WORK"]
                if is_admin:
                    available_categories.extend(["LEAVE", "HOLIDAY"])
                
                category = st.selectbox("일정 유형", available_categories, format_func=lambda x: "일반 업무" if x=="WORK" else ("휴부 일정" if x=="LEAVE" else "사내 공휴일/오봉"))
                submitted = st.form_submit_button("등록")
                
                if submitted and title:
                    supabase.table("schedules").insert({
                        "title": title,
                        "schedule_date": str(s_date),
                        "category": category,
                        "created_by": user["id"]
                    }).execute()
                    st.success("일정이 등록되었습니다.")
                    st.rerun()

        # 전체 일정 조회
        schedules = supabase.table("schedules").select("*").execute()
        if schedules.data:
            st.dataframe(schedules.data, use_container_width=True)

    with tab2:
        st.subheader("휴무 신청")
        with st.form("leave_request_form"):
            leave_type = st.selectbox("휴무 종류", ["연차", "오전반차", "오후반차", "경조사"])
            start_date = st.date_input("시작일")
            end_date = st.date_input("종료일")
            reason = st.text_area("사유")
            submitted = st.form_submit_button("휴무 신청 제출")
            
            if submitted:
                supabase.table("leaves").insert({
                    "user_id": user["id"],
                    "leave_type": leave_type,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "reason": reason,
                    "status": "PENDING"
                }).execute()
                st.success("휴무 신청이 완료되었습니다.")

        # 관리자 전용 승인 목록
        if is_admin:
            st.markdown("---")
            st.subheader("⚡ [관리자] 휴무 승인 처리")
            pending_leaves = supabase.table("leaves").select("*, user_profiles(full_name)").eq("status", "PENDING").execute()
            
            for leave in pending_leaves.data:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{leave['user_profiles']['full_name']}**: {leave['leave_type']} ({leave['start_date']} ~ {leave['end_date']}) - {leave['reason']}")
                with col2:
                    if st.button("승인", key=f"app_{leave['id']}"):
                        # 1. 휴무 승인
                        supabase.table("leaves").update({"status": "APPROVED"}).eq("id", leave["id"]).execute()
                        # 2. 캘린더에 자동 등록
                        supabase.table("schedules").insert({
                            "title": f"🚩 [휴무] {leave['user_profiles']['full_name']} ({leave['leave_type']})",
                            "schedule_date": leave["start_date"],
                            "category": "LEAVE",
                            "created_by": user["id"],
                            "user_id": leave["user_id"]
                        }).execute()
                        st.success("승인 완료 및 캘린더 반영!")
                        st.rerun()
                with col3:
                    if st.button("거절", key=f"rej_{leave['id']}"):
                        supabase.table("leaves").update({"status": "REJECTED"}).eq("id", leave["id"]).execute()
                        st.rerun()
