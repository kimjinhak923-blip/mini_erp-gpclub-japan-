import streamlit as st

st.set_page_config(
    page_title="사내 통합 관리 시스템 (ERP)",
    page_layout="wide",
    initial_sidebar_state="expanded",
)

# --- 기본 세션 데이터 초기화 (기존 기능 100% 보존 + 신규 기능 세션) ---
if "lang" not in st.session_state:
    st.session_state.lang = "한국어"

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "users" not in st.session_state:
    st.session_state.users = [
        {
            "id": "admin",
            "pw": "admin1234",
            "name": "관리자",
            "role": "CEO / 관리자",
            "position": "대표이사",
            "approved": True,
            "hire_date": "2020-01-01",
            "remaining_leave": 15,
        },
        {
            "id": "user1",
            "pw": "1234",
            "name": "김사원",
            "role": "일반 사용자",
            "position": "사원",
            "approved": True,
            "hire_date": "2023-03-01",
            "remaining_leave": 12,
        },
    ]

if "warehouses" not in st.session_state:
    st.session_state.warehouses = ["SAGAWA", "L&K", "大吉商事"]

if "positions" not in st.session_state:
    st.session_state.positions = ["대표이사", "이사", "부장", "차장", "과장", "대리", "사원"]

if "master_products" not in st.session_state:
    st.session_state.master_products = [
        {
            "jan_code": "4580000000001",
            "product_name": "프리미엄 수분 크림 50ml",
            "category": "스킨케어",
            "capacity": "50ml",
            "units_per_box": 24,
            "box_cbm": 0.02,
            "box_weight_kg": 8.5,
            "plt_qty": 40,
            "supply_price_jpy": 1200,
            "list_price_jpy": 2500,
            "memo": "주력 상품",
        }
    ]

# 신규: 집기 마스터 세션
if "master_fixtures" not in st.session_state:
    st.session_state.master_fixtures = [
        {
            "fixture_name": "아크릴 매대 A타입",
            "total_qty": 100,
            "remaining_qty": 80,
            "warehouse": "SAGAWA",
            "total_cost": 500000,
            "unit_cost": 5000,
            "total_remaining_value": 400000,
        }
    ]

if "warehouse_stocks" not in st.session_state:
    st.session_state.warehouse_stocks = [
        {"warehouse": "SAGAWA", "jan_code": "4580000000001", "product_name": "프리미엄 수분 크림 50ml", "stock_qty": 150}
    ]

if "clients" not in st.session_state:
    st.session_state.clients = [
        {
            "client_name": "(주)파트너스 코리아",
            "business_type": "도매",
            "contact_person": "이팀장",
            "phone": "03-1234-5678",
            "email": "partner@example.com",
            "postal_code": "100-0001",
            "address": "東京都千代田区1-1",
        }
    ]

if "client_products" not in st.session_state:
    st.session_state.client_products = []

if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = []

if "leave_records" not in st.session_state:
    st.session_state.leave_records = []

if "company_holidays" not in st.session_state:
    st.session_state.company_holidays = []

# --- 로그인 / 회원가입 UI ---
if not st.session_state.logged_in_user:
    st.title("🏢 사내 통합 관리 시스템")
    st.markdown("---")

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.subheader("🔐 인증 센터")
        tab_l, tab_s = st.tabs(["로그인", "회원가입"])

        with tab_l:
            login_id = st.text_input("사원번호 또는 아이디", key="main_login_id")
            login_pw = st.text_input("비밀번호", type="password", key="main_login_pw")
            if st.button("로그인", use_container_width=True, type="primary"):
                user = next((u for u in st.session_state.users if u["id"] == login_id and u["pw"] == login_pw), None)
                if user:
                    if not user.get("approved", True):
                        st.error("아직 관리자 승인이 완료되지 않은 계정입니다.")
                    else:
                        st.session_state.logged_in_user = user
                        st.switch_page("pages/01_⏱️_출퇴근시스템.py")
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

        with tab_s:
            new_id = st.text_input("아이디 (ID)", key="main_su_id")
            new_pw = st.text_input("비밀번호 (PW)", type="password", key="main_su_pw")
            new_name = st.text_input("이름 (성명)", key="main_su_name")
            if st.button("가입 신청", use_container_width=True):
                if new_id and new_pw and new_name:
                    st.session_state.users.append({
                        "id": new_id,
                        "pw": new_pw,
                        "name": new_name,
                        "role": "일반 사용자",
                        "position": "사원",
                        "approved": False,
                        "hire_date": "2026-01-01",
                        "remaining_leave": 10,
                    })
                    st.success("회원가입 신청이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.")
                else:
                    st.error("모든 항목을 입력해주세요.")
else:
    st.switch_page("pages/01_⏱️_출퇴근시스템.py")
