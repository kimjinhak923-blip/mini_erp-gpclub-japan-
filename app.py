import streamlit as st
from views import auth, dashboard, master_data, sales, inventory, invoice, attendance, calendar_leave, staff

st.set_page_config(page_title="통합 ERP 시스템", layout="wide")

if "user" not in st.session_state:
    st.sidebar.title("🏢 로그인 / 회원가입")
    auth_mode = st.sidebar.radio("선택", ["로그인", "회원가입"])
    if auth_mode == "로그인":
        auth.render_login()
    else:
        auth.render_signup()
else:
    user = st.session_state["user"]
    st.sidebar.title(f"👤 {user['full_name']} ({user['role']})")
    
    if st.sidebar.button("로그아웃"):
        del st.session_state["user"]
        st.rerun()
        
    menu_options = ["📊 경영 대시보드", "출퇴근 관리", "캘린더 & 휴무", "마스터 데이터", "영업 및 배송", "재고 관리", "청구 및 정산"]
    if user["role"] == "ADMIN":
        menu_options.append("직원 승인 관리")
        
    menu = st.sidebar.radio("메뉴 선택", menu_options)

    if menu == "📊 경영 대시보드":
        dashboard.render()
    elif menu == "출퇴근 관리":
        attendance.render()
    elif menu == "캘린더 & 휴무":
        calendar_leave.render()
    elif menu == "마스터 데이터":
        master_data.render()
    elif menu == "영업 및 배송":
        sales.render()
    elif menu == "재고 관리":
        inventory.render()
    elif menu == "청구 및 정산":
        invoice.render()
    elif menu == "직원 승인 관리":
        staff.render()
