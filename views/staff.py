import streamlit as st
from utils.supabase_client import supabase

def render():
    st.header("👥 직원 및 회원가입 승인 관리")
    user = st.session_state.get("user")
    
    if user["role"] != "ADMIN":
        st.error("관리자(ADMIN) 전용 페이지입니다.")
        return

    st.subheader("⏳ 가입 대기 중인 계정 승인")
    pending_users = supabase.table("user_profiles").select("*").eq("status", "PENDING").execute()
    
    if pending_users.data:
        for p_user in pending_users.data:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    st.write(f"**{p_user['full_name']}** (`{p_user['username']}`)")
                with col2:
                    # 관리자가 승인 시 권한을 변경 지정 가능
                    assigned_role = st.selectbox(
                        "부여 권한",
                        ["GUEST", "STAFF", "ADMIN"],
                        index=["GUEST", "STAFF", "ADMIN"].index(p_user.get("role", "GUEST")),
                        key=f"role_sel_{p_user['id']}"
                    )
                with col3:
                    if st.button("승인", key=f"approve_{p_user['id']}"):
                        supabase.table("user_profiles").update({
                            "status": "APPROVED",
                            "role": assigned_role
                        }).eq("id", p_user["id"]).execute()
                        st.success(f"'{p_user['full_name']}' 님 ({assigned_role}) 승인 완료!")
                        st.rerun()
                with col4:
                    if st.button("거절", key=f"reject_{p_user['id']}"):
                        supabase.table("user_profiles").update({"status": "REJECTED"}).eq("id", p_user["id"]).execute()
                        st.rerun()
                st.markdown("---")
    else:
        st.info("현재 대기 중인 회원가입 요청이 없습니다.")
