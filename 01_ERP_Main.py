import datetime
import pytz
import streamlit as st

# ⚠️ 반드시 streamlit 관련 코드 중 가장 첫 번째로 실행되어야 합니다!
st.set_page_config(
    page_title="사내 통합 관리 시스템 (ERP)",
    page_layout="wide",
    initial_sidebar_state="expanded",
)

# 그 아래에 CSS 및 나머지 로직 실행
st.markdown("""
    <style>
        .main .block-container {
            max-width: 98% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1.5rem !important;
        }
        .stDataFrame, div[data-testid="stTable"] {
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# ... (이후 동일)

# ==========================================
# 0. 레이아웃 설정 및 가로 폭 최대화 CSS
# ==========================================
st.set_page_config(
    page_title="사내 통합 관리 시스템 (ERP)",
    page_layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
        /* 메인 컨테이너 폭 최대화 및 여백 축소 */
        .main .block-container {
            max-width: 98% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1.5rem !important;
        }
        /* 테이블/데이터프레임 영역 가로 확장 */
        .stDataFrame, div[data-testid="stTable"] {
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 다국어 딕셔너리 설정
# ==========================================
LANG_PACK = {
    "한국어": {
        "title": "🏢 사내 통합 관리 시스템",
        "lang_select": "🌐 언어 선택 / Language",
        "user_info": "접속자",
        "role_info": "권한",
        "logout": "🚪 로그아웃",
        "tokyo_time": "도쿄 기준 시간 (Asia/Tokyo)",
    },
    "日本語": {
        "title": "🏢 社内統合管理システム",
        "lang_select": "🌐 言語選択 / Language",
        "user_info": "ログインユーザー",
        "role_info": "権限",
        "logout": "🚪 ログアウト",
        "tokyo_time": "東京基準時間 (Asia/Tokyo)",
    },
    "English": {
        "title": "🏢 Integrated ERP System",
        "lang_select": "🌐 Select Language",
        "user_info": "Logged in as",
        "role_info": "Role",
        "logout": "🚪 Logout",
        "tokyo_time": "Tokyo Time (Asia/Tokyo)",
    },
}

# ==========================================
# 2. 공통 세션 상태(데이터베이스) 초기화
# ==========================================
if "lang" not in st.session_state:
    st.session_state.lang = "한국어"

L = LANG_PACK[st.session_state.lang]

if "users" not in st.session_state:
    st.session_state.users = [
        {
            "id": "admin",
            "pw": "admin123",
            "name": "관리자",
            "position": "팀장",
            "dept": "경영관리팀",
            "role": "관리자",
            "status": "승인 완료",
            "hire_date": "2024-01-01",
            "annual_leave": 15.0,
        }
    ]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "warehouses" not in st.session_state:
    st.session_state.warehouses = ["SAGAWA", "L&K", "大吉商事"]

if "positions" not in st.session_state:
    st.session_state.positions = ["사원", "주임", "대리", "과장", "차장", "부장", "팀장", "이사", "법인장"]

if "roles" not in st.session_state:
    st.session_state.roles = ["관리자", "STAFF", "방문자"]

if "master_products" not in st.session_state:
    st.session_state.master_products = [
        {
            "code": "PRD-1001",
            "name": "샘플 마스크팩",
            "jan_pack": "4901234567890",
            "jan_single": "4901234567891",
            "capacity": "10매/곽",
            "category": "화장품/뷰티",
            "price": 3000,
            "in_pack_qty": "1곽/10장",
            "prod_size": "15x20x3cm",
            "box_size": "40x30x20cm",
            "plt_qty": "50박스",
            "vendor": "大吉商事",
        }
    ]

if "warehouse_stocks" not in st.session_state:
    st.session_state.warehouse_stocks = {
        "PRD-1001_SAGAWA": 50,
        "PRD-1001_L&K": 30,
        "PRD-1001_大吉商事": 20,
    }

if "clients" not in st.session_state:
    st.session_state.clients = [
        {
            "id": 1,
            "name": "(주)도쿄유통",
            "zipcode": "100-0001",
            "address": "東京都千代田区1-1",
            "phone": "03-1234-5678",
        }
    ]

if "client_products" not in st.session_state:
    st.session_state.client_products = [
        {
            "id": 1,
            "client_name": "(주)도쿄유통",
            "prod_name": "샘플 마스크팩",
            "jan_pack": "4901234567890",
            "jan_single": "4901234567891",
            "supply_price": 4500,
        }
    ]

if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = [
        {
            "po_no": "PO-20260812-01",
            "date": "2026-08-12",
            "type": "출고",
            "wh": "SAGAWA",
            "client": "(주)도쿄유통",
            "prod_name": "샘플 마스크팩",
            "jan": "4901234567890",
            "qty": 10,
            "unit_price": 4500,
            "total_price": 45000,
            "trade_type": "납품",
            "manager": "관리자",
            "zipcode": "100-0001",
            "ship_to": "(주)도쿄유통 / 東京都千代田区1-1 / 03-1234-5678",
        }
    ]

if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = []

if "leave_records" not in st.session_state:
    st.session_state.leave_records = []

if "company_holidays" not in st.session_state:
    st.session_state.company_holidays = [
        {"id": 1, "date": "2026-01-01", "title": "元日 (신정)", "type": "일본 공휴일"},
        {"id": 2, "date": "2026-01-12", "title": "成人の日 (성인의 날)", "type": "일본 공휴일"},
        {"id": 3, "date": "2026-02-11", "title": "建国記念の日 (건국기념일)", "type": "일본 공휴일"},
        {"id": 4, "date": "2026-02-23", "title": "天皇誕生日 (천황탄생일)", "type": "일본 공휴일"},
        {"id": 5, "date": "2026-05-03", "title": "憲法記念日 (헌법기념일)", "type": "일본 공휴일"},
        {"id": 6, "date": "2026-08-11", "title": "山の日 (산의 날)", "type": "일본 공휴일"},
        {"id": 7, "date": "2026-11-03", "title": "文化の日 (문화의 날)", "type": "일본 공휴일"},
        {"id": 8, "date": "2026-11-23", "title": "勤労感謝の日 (근로감사의 날)", "type": "일본 공휴일"},
    ]

# ==========================================
# 3. 사이드바 글로벌 옵션
# ==========================================
st.sidebar.selectbox("🌐 Language / 언어", ["한국어", "日本語", "English"], key="lang")

def get_tokyo_time():
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    return datetime.datetime.now(tokyo_tz)

tokyo_now = get_tokyo_time()

# ==========================================
# 4. 로그인 화면 및 메인 인트로
# ==========================================
if st.session_state.logged_in_user is None:
    st.title(L["title"])
    tab_login, tab_register = st.tabs(["🔑 로그인 / Login", "📝 계정 신청 / Register"])

    with tab_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                input_id = st.text_input("ID")
                input_pw = st.text_input("Password", type="password")
                submit = st.form_submit_button("로그인", use_container_width=True)

                if submit:
                    user = next((u for u in st.session_state.users if u["id"] == input_id and u["pw"] == input_pw), None)
                    if user:
                        if user.get("status") == "승인 대기":
                            st.warning("계정 승인 대기 중입니다.")
                        else:
                            st.session_state.logged_in_user = user
                            st.success(f"{user['name']}님 환영합니다!")
                            st.rerun()
                    else:
                        st.error("ID 또는 비밀번호가 잘못되었습니다.")

    with tab_register:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                st.subheader("신규 계정 신청")
                reg_id = st.text_input("아이디 *")
                reg_pw = st.text_input("비밀번호 *", type="password")
                reg_name = st.text_input("이름 *")
                reg_dept = st.text_input("부서 *", value="영업팀")
                reg_position = st.selectbox("직급 *", st.session_state.positions)
                reg_role = st.selectbox("신청 권한 *", st.session_state.roles)

                if st.form_submit_button("신청 제출", use_container_width=True):
                    if not reg_id or not reg_pw or not reg_name:
                        st.error("필수 항목을 모두 입력해주세요.")
                    elif any(u["id"] == reg_id for u in st.session_state.users):
                        st.error("이미 존재하는 아이디입니다.")
                    else:
                        st.session_state.users.append({
                            "id": reg_id,
                            "pw": reg_pw,
                            "name": reg_name,
                            "position": reg_position,
                            "dept": reg_dept,
                            "role": reg_role,
                            "status": "승인 완료" if reg_role == "방문자" else "승인 대기",
                            "hire_date": str(datetime.date.today()),
                            "annual_leave": 15.0,
                        })
                        st.success("신청이 완료되었습니다.")
else:
    user = st.session_state.logged_in_user
    st.sidebar.write(f"**{L['user_info']}:** {user['name']} ({user['position']})")
    st.sidebar.write(f"**{L['role_info']}:** {user['role']} {'👑' if user['role']=='관리자' else ''}")

    if st.sidebar.button(L["logout"], use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

    st.title("🏢 ERP 메인 대시보드 홈")
    st.info(f"🕒 **{L['tokyo_time']}:** {tokyo_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    st.success(f"안녕하세요, **{user['name']}**님! 좌측 사이드바 메뉴를 선택하여 각 독립 기능으로 이동하세요.")
