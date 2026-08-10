import streamlit as st
from utils.supabase_client import supabase

def render():
    st.header("👥 직원 및 승인 관리")
    user = st.session_state.get("user")
    
    if user["role"] != "ADMIN":
        st.error("관리자 전용 페이지입니다.")
        return

    st.subheader("⏳ 가입 대기 중인 직원 승인")
    pending_users = supabase.table("user_profiles").select("*").eq("status", "PENDING").execute()
    
    if pending_users.data:
        for p_user in pending_users.data:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{p_user['full_name']}** ({p_user['username']})")
            with col2:
                if st.button("승인", key=f"approve_{p_user['id']}"):
                    supabase.table("user_profiles").update({"status": "APPROVED"}).eq("id", p_user["id"]).execute()
                    st.success("승인되었습니다.")
                    st.rerun()
            with col3:
                if st.button("거절", key=f"reject_{p_user['id']}"):
                    supabase.table("user_profiles").update({"status": "REJECTED"}).eq("id", p_user["id"]).execute()
                    st.rerun()
    else:
        st.info("대기 중인 회원가입 요청이 없습니다.")
