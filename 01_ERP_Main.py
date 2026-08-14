import streamlit as st
from i18n import txt, render_live_clock  # 공통 다국어 및 실시간 시계 모듈 로드

# ⚠️ page_layout -> layout 으로 파라미터명 수정 완료
st.set_page_config(
    page_title="사내 통합 관리 시스템 (ERP)",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 기본 세션 데이터 초기화 (기능 100% 보존) ---
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
            "lang": "한국어",  # 기본 언어 설정
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
            "lang": "한국어",  # 기본 언어 설정
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
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title(txt("system_title"))
    with col_h2:
        st.markdown(f"**{txt('live_clock')}**")
        render_live_clock()

    st.markdown("---")

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.subheader(txt("auth_center"))
        tab_l, tab_s = st.tabs([txt("login"), txt("signup")])

        with tab_l:
            login_id = st.text_input(txt("user_id"), key="main_login_id")
            login_pw = st.text_input(txt("password"), type="password", key="main_login_pw")
            if st.button(txt("login"), use_container_width=True, type="primary"):
                user = next((u for u in st.session_state.users if u["id"] == login_id and u["pw"] == login_pw), None)
                if user:
                    if not user.get("approved", True):
                        st.error(txt("pending_approval"))
                    else:
                        # 로그인 유저 설정 및 계정 기본 언어로 즉시 전환
                        st.session_state.logged_in_user = user
                        st.session_state.lang = user.get("lang", "한국어")
                        st.switch_page("pages/01_⏱️_출퇴근시스템.py")
                else:
                    st.error(txt("login_fail"))

        with tab_s:
            new_id = st.text_input("아이디 (ID)", key="main_su_id")
            new_pw = st.text_input(f"{txt('password')} (PW)", type="password", key="main_su_pw")
            new_name = st.text_input(txt("name"), key="main_su_name")
            # 회원가입 시 선호 언어 선택 기능 추가
            new_lang = st.selectbox(txt("preferred_lang"), ["한국어", "English", "日本語"], key="main_su_lang")
            
            if st.button(txt("signup_btn"), use_container_width=True):
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
                        "lang": new_lang,  # 가입 시 선택한 기본 언어 저장
                    })
                    st.success(txt("signup_success"))
                else:
                    st.error(txt("fill_all"))
else:
    # 이미 로그인되어 있다면 계정 언어로 세션 보장 후 이동
    st.session_state.lang = st.session_state.logged_in_user.get("lang", st.session_state.lang)
    st.switch_page("pages/01_⏱️_출퇴근시스템.py")
