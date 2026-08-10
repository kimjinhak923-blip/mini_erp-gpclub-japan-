import streamlit as st
from views import auth, dashboard, master_data, sales, inventory, invoice, attendance, calendar_leave, staff

st.set_page_config(page_title="통합 ERP 시스템", layout="wide")

# 브라우저 새로고침 시 자동 로그인 체크
auth.check_auto_login()

if "user" not in st.session_state:
    st.sidebar.title("🏢 로그인 / 회원가입")
    auth_mode = st.sidebar.radio("선택", ["로그인", "회원가입"])
    if auth_mode == "로그인":
        auth.render_login()
    else:
        auth.render_signup()
else:
    user = st.session_state["user"]
    role_label = {
        "ADMIN": "👑 관리자",
        "STAFF": "👔 사원",
        "GUEST": "👀 방문자"
    }.get(user["role"], user["role"])
    
    st.sidebar.title(f"{role_label} {user['full_name']}님")
    
    if st.sidebar.button("🚪 로그아웃"):
        auth.clear_login_session()
        st.rerun()
        
    menu_options = ["📊 경영 대시보드", "출퇴근 관리", "캘린더 & 휴무", "마스터 데이터", "영업 및 배송", "재고 관리", "청구 및 정산"]
    
    # 직원 관리 메뉴는 관리자만 노출
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
