import datetime
import pytz
import streamlit as st

# ----------------------------------------------------
# 0. Streamlit 설정 (Cloud 환경 중복 호출 방지 적용)
# ----------------------------------------------------
try:
    st.set_page_config(
        page_title="사내 통합 관리 시스템 (ERP)",
        page_layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

# 화면 가로폭 최대화 CSS 적용
st.markdown("""
    <style>
        .main .block-container {
            max-width: 98% !important;
            padding-left: 1rem !important;
            padding-right: 1.5rem !important;
            padding-top: 1.5rem !important;
        }
        .stDataFrame, div[data-testid="stTable"] {
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. 다국어 딕셔너리 설정
# ----------------------------------------------------
LANG_PACK = {
    "한국어": {
        "title": "🏢 사내 통합 관리 시스템",
        "lang_select": "🌐 언어 선택 / Language",
        "user_info": "접속자",
        "role_info": "권한",
        "logout": "🚪 로그아웃",
        "tokyo_time": "도쿄 기준 시간 (Asia/Tokyo)",
        "login_req": "로그인이 필요합니다.",
        "id_ph": "사원번호 또는 아이디",
        "pw_ph": "비밀번호",
        "login_btn": "로그인",
        "login_fail": "아이디 또는 비밀번호가 올바르지 않습니다.",
        "signup_tab": "회원가입",
        "login_tab": "로그인",
        "signup_btn": "가입 신청",
        "signup_success": "회원가입 신청이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.",
        "not_approved": "아직 관리자 승인이 완료되지 않은 계정입니다.",
    },
    "日本語": {
        "title": "🏢 社内統合管理システム",
        "lang_select": "🌐 言語選択 / Language",
        "user_info": "ログインユーザー",
        "role_info": "権限",
        "logout": "🚪 ログアウト",
        "tokyo_time": "東京基準時間 (Asia/Tokyo)",
        "login_req": "ログインしてください。",
        "id_ph": "社員番号またはID",
        "pw_ph": "パスワード",
        "login_btn": "ログイン",
        "login_fail": "IDまたはパスワードが正しくありません。",
        "signup_tab": "新規登録",
        "login_tab": "ログイン",
        "signup_btn": "登録申請",
        "signup_success": "登録申請が完了しました。管理者の承認後にログインできます。",
        "not_approved": "まだ管理者の承認が完了していないアカウントです。",
    },
    "English": {
        "title": "🏢 Integrated ERP System",
        "lang_select": "🌐 Select Language",
        "user_info": "Logged in as",
        "role_info": "Role",
        "logout": "🚪 Logout",
        "tokyo_time": "Tokyo Time (Asia/Tokyo)",
        "login_req": "Please log in to continue.",
        "id_ph": "Employee ID or Username",
        "pw_ph": "Password",
        "login_btn": "Login",
        "login_fail": "Invalid ID or Password.",
        "signup_tab": "Sign Up",
        "login_tab": "Login",
        "signup_btn": "Register",
        "signup_success": "Registration requested. You can log in after admin approval.",
        "not_approved": "Account pending admin approval.",
    },
}

# ----------------------------------------------------
# 2. 공통 세션 상태(데이터베이스 시뮬레이션) 초기화
# ----------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "한국어"

if "users" not in st.session_state:
    st.session_state.users = [
        {
            "id": "admin",
            "pw": "admin1234",
            "name": "관리자",
            "role": "CEO / 관리자",
            "position": "대표이사",
            "approved": True,
            "hire_date": "2023-01-01",
            "remaining_leave": 15,
        },
        {
            "id": "user1",
            "pw": "1234",
            "name": "김사원",
            "role": "일반 사용자",
            "position": "사원",
            "approved": True,
            "hire_date": "2024-03-01",
            "remaining_leave": 12,
        },
    ]

if "positions" not in st.session_state:
    st.session_state.positions = ["대표이사", "이사", "부장", "과장", "대리", "사원"]

if "roles" not in st.session_state:
    st.session_state.roles = ["CEO / 관리자", "일반 사용자"]

if "warehouses" not in st.session_state:
    st.session_state.warehouses = ["도쿄 본사 창고", "오사카 물류 센터", "치바 냉장 창고"]

if "master_products" not in st.session_state:
    st.session_state.master_products = [
        {
            "jan_code": "8801234567890",
            "product_name": "프리미엄 수분 크림 50ml",
            "category": "스킨케어",
            "capacity": "50ml",
            "units_per_box": 24,
            "box_cbm": 0.025,
            "box_weight_kg": 12.0,
            "plt_qty": 40,
            "supply_price_jpy": 1500,
            "list_price_jpy": 3000,
            "memo": "주력 상품",
        },
        {
            "jan_code": "8801234567891",
            "product_name": "비타민 C 세럼 30ml",
            "category": "스킨케어",
            "capacity": "30ml",
            "units_per_box": 36,
            "box_cbm": 0.020,
            "box_weight_kg": 10.0,
            "plt_qty": 48,
            "supply_price_jpy": 2000,
            "list_price_jpy": 4000,
            "memo": "인기 급상승",
        },
    ]

if "warehouse_stocks" not in st.session_state:
    st.session_state.warehouse_stocks = [
        {
            "warehouse": "도쿄 본사 창고",
            "jan_code": "8801234567890",
            "product_name": "프리미엄 수분 크림 50ml",
            "stock_qty": 1200,
        },
        {
            "warehouse": "도쿄 본사 창고",
            "jan_code": "8801234567891",
            "product_name": "비타민 C 세럼 30ml",
            "category": "스킨케어",
            "capacity": "30ml",
            "units_per_box": 36,
            "stock_qty": 800,
        },
        {
            "warehouse": "오사카 물류 센터",
            "jan_code": "8801234567890",
            "product_name": "프리미엄 수분 크림 50ml",
            "stock_qty": 500,
        },
    ]

if "clients" not in st.session_state:
    st.session_state.clients = [
        {
            "client_name": "도쿄 코스메틱스",
            "business_type": "도매",
            "contact_person": "다나카 상",
            "phone": "03-1234-5678",
            "email": "tanaka@tokyocos.jp",
            "postal_code": "100-0001",
            "address": "도쿄도시 치요다구 1-1",
        },
        {
            "client_name": "오사카 뷰티샵",
            "business_type": "소매",
            "contact_person": "사토 상",
            "phone": "06-9876-5432",
            "email": "sato@osakabeauty.jp",
            "postal_code": "530-0001",
            "address": "오사카시 키타구 우메다 2-2",
        },
    ]

if "client_products" not in st.session_state:
    st.session_state.client_products = [
        {
            "client_name": "도쿄 코스메틱스",
            "jan_code": "8801234567890",
            "product_name": "프리미엄 수분 크림 50ml",
            "custom_supply_price": 1400,
        }
    ]

if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = []

if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = []

if "leave_records" not in st.session_state:
    st.session_state.leave_records = []

if "company_holidays" not in st.session_state:
    st.session_state.company_holidays = []

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ----------------------------------------------------
# 3. 사이드바 - 언어 및 로그인 상태 제어
# ----------------------------------------------------
st.sidebar.title("🌍 시스템 설정")
selected_lang = st.sidebar.selectbox(
    "🌐 언어 선택 / Language",
    ["한국어", "日本語", "English"],
    index=["한국어", "日本語", "English"].index(st.session_state.get("lang", "한국어")),
)
st.session_state.lang = selected_lang
t = LANG_PACK[selected_lang]

st.sidebar.markdown("---")

# 로그인 안 된 상태
if not st.session_state.logged_in_user:
    st.sidebar.subheader("🔐 로그인 / 회원가입")
    tab_l, tab_s = st.sidebar.tabs([t["login_tab"], t["signup_tab"]])

    with tab_l:
        login_id = st.text_input(t["id_ph"], key="login_id_input")
        login_pw = st.text_input(t["pw_ph"], type="password", key="login_pw_input")
        if st.button(t["login_btn"], key="main_login_btn"):
            found = False
            for u in st.session_state.users:
                if u["id"] == login_id and u["pw"] == login_pw:
                    found = True
                    if not u["approved"]:
                        st.sidebar.error(t["not_approved"])
                    else:
                        st.session_state.logged_in_user = u
                        st.sidebar.success(f"환영합니다, {u['name']}님!")
                        st.rerun()
                    break
            if not found:
                st.sidebar.error(t["login_fail"])

    with tab_s:
        new_id = st.text_input("아이디 (ID)", key="su_id")
        new_pw = st.text_input("비밀번호 (PW)", type="password", key="su_pw")
        new_name = st.text_input("이름 (성명)", key="su_name")
        new_pos = st.selectbox("직급", st.session_state.positions, key="su_pos")
        if st.button(t["signup_btn"], key="main_signup_btn"):
            if not new_id or not new_pw or not new_name:
                st.sidebar.error("모든 항목을 입력해주세요.")
            else:
                exists = any(u["id"] == new_id for u in st.session_state.users)
                if exists:
                    st.sidebar.error("이미 존재하는 아이디입니다.")
                else:
                    st.session_state.users.append({
                        "id": new_id,
                        "pw": new_pw,
                        "name": new_name,
                        "role": "일반 사용자",
                        "position": new_pos,
                        "approved": False,
                        "hire_date": str(datetime.date.today()),
                        "remaining_leave": 15,
                    })
                    st.sidebar.success(t["signup_success"])

    st.stop()  # 로그인 전에는 메인 화면 진입 차단

# 로그인 된 상태 - 사이드바 정보 표시
user = st.session_state.logged_in_user
st.sidebar.markdown(f"👤 **{t['user_info']}**: {user['name']} ({user['position']})")
st.sidebar.markdown(f"🔑 **{t['role_info']}**: {user['role']}")

tokyo_tz = pytz.timezone("Asia/Tokyo")
current_tokyo_time = datetime.datetime.now(tokyo_tz).strftime("%Y-%m-%d %H:%M:%S")
st.sidebar.info(f"🕒 {t['tokyo_time']}\n\n**{current_tokyo_time}**")

if st.sidebar.button(t["logout"], key="main_logout_btn"):
    st.session_state.logged_in_user = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 메뉴 안내")
st.sidebar.info("왼쪽 상단의 메뉴(> 버튼)에서 원하는 페이지로 이동하세요.")

# ----------------------------------------------------
# 4. 메인 대시보드 홈 화면
# ----------------------------------------------------
st.title(t["title"])
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="등록된 마스터 상품", value=f"{len(st.session_state.master_products)} 개")
with col2:
    total_stock_qty = sum(item["stock_qty"] for item in st.session_state.warehouse_stocks)
    st.metric(label="총 재고 수량", value=f"{total_stock_qty:,} 개")
with col3:
    st.metric(label="등록된 거래처", value=f"{len(st.session_state.clients)} 개")
with col4:
    st.metric(label="총 입출고 이력", value=f"{len(st.session_state.stock_logs)} 건")

st.success(f"👋 **{user['name']}**님, 반갑습니다! 좌측 사이드바의 멀티페이지 메뉴에서 필요한 업무 화면을 선택하여 이용해 주세요.")

st.markdown("---")
st.markdown("### 📊 창고별 재고 현황 요약")
if st.session_state.warehouse_stocks:
    import pandas as pd
    df_stock = pd.DataFrame(st.session_state.warehouse_stocks)
    st.dataframe(df_stock, use_container_width=True)
else:
    st.info("등록된 재고 데이터가 없습니다.")
