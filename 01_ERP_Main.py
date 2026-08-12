import datetime
import calendar
import pandas as pd
import pytz
import streamlit as st

# ==========================================
# 0. 최상단 배치 (Telemetry 예외 안전 처리)
# ==========================================
try:
    st.set_page_config(
        page_title="사내 통합 관리 시스템 (ERP)",
        page_layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

# ==========================================
# 1. 다국어 딕셔너리 설정 (한국어 / 日本語 / English)
# ==========================================
LANG_PACK = {
    "한국어": {
        "title": "🏢 사내 통합 관리 시스템",
        "lang_select": "🌐 언어 선택 / Language",
        "user_info": "접속자",
        "role_info": "권한",
        "logout": "🚪 로그아웃",
        "menu": "메뉴 이동",
        "tokyo_time": "도쿄 기준 시간 (Asia/Tokyo)",
        "mypage": "👤 마이페이지",
        "dashboard": "📊 대시보드",
        "attendance": "⏱️ 출퇴근시스템(현황)",
        "master_prod": "📦 마스터 상품 등록/관리",
        "client_mgmt": "🤝 거래처 관리",
        "stock_mgmt": "🔄 재고관리 (입고/출고)",
        "stock_history": "📜 입출고 이력 조회",
        "sales_mgmt": "💰 매출 관리",
        "timecard": "📆 타임카드 (휴가/일정)",
        "sys_mgmt": "⚙️ 시스템 관리 (사용자/권한)",
        "search": "검색 (상품명, 바코드, 발주번호)",
        "warehouse": "창고",
        "client": "거래처",
        "date_range": "기간 선택",
    },
    "日本語": {
        "title": "🏢 社内統合管理システム",
        "lang_select": "🌐 言語選択 / Language",
        "user_info": "ログインユーザー",
        "role_info": "権限",
        "logout": "🚪 ログアウト",
        "menu": "メニュー移動",
        "tokyo_time": "東京基準時間 (Asia/Tokyo)",
        "mypage": "👤 マイページ",
        "dashboard": "📊 ダッシュボード",
        "attendance": "⏱️ 勤怠管理システム",
        "master_prod": "📦 マスター商品登録/管理",
        "client_mgmt": "🤝 取引先管理",
        "stock_mgmt": "🔄 在庫管理 (入庫/出庫)",
        "stock_history": "📜 入出庫履歴照会",
        "sales_mgmt": "💰 売上管理",
        "timecard": "📆 タイムカード (休暇/日程)",
        "sys_mgmt": "⚙️ システム管理 (ユーザー/権限)",
        "search": "検索 (商品名、バーコード、発注番号)",
        "warehouse": "倉庫",
        "client": "取引先",
        "date_range": "期間選択",
    },
    "English": {
        "title": "🏢 Integrated ERP System",
        "lang_select": "🌐 Select Language",
        "user_info": "Logged in as",
        "role_info": "Role",
        "logout": "🚪 Logout",
        "menu": "Navigation",
        "tokyo_time": "Tokyo Time (Asia/Tokyo)",
        "mypage": "👤 My Page",
        "dashboard": "📊 Dashboard",
        "attendance": "⏱️ Attendance System",
        "master_prod": "📦 Master Product Management",
        "client_mgmt": "🤝 Client Management",
        "stock_mgmt": "🔄 Inventory Management",
        "stock_history": "📜 Stock History",
        "sales_mgmt": "💰 Sales Management",
        "timecard": "📆 Timecard & Calendar",
        "sys_mgmt": "⚙️ System Management",
        "search": "Search (Name, Barcode, PO No.)",
        "warehouse": "Warehouse",
        "client": "Client",
        "date_range": "Date Range",
    },
}

# ==========================================
# 2. 세션 상태(데이터베이스) 초기화
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

WAREHOUSES = ["SAGAWA", "L&K", "大吉商事"]
POSITIONS = ["사원", "주임", "대리", "과장", "차장", "부장", "팀장", "이사", "법인장"]
ROLES = ["관리자", "STAFF", "방문자"]

if "categories" not in st.session_state:
    st.session_state.categories = ["전자기기", "사무용품", "소모품", "가구/집기", "화장품/뷰티"]

# 마스터 상품
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

# 창고별 재고
if "warehouse_stocks" not in st.session_state:
    st.session_state.warehouse_stocks = {
        "PRD-1001_SAGAWA": 50,
        "PRD-1001_L&K": 30,
        "PRD-1001_大吉商事": 20,
    }

# 거래처
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

# 거래처별 상품
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

# 입출고 이력
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

# 일본 공휴일 및 일정 데이터 (수정/삭제 가능)
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


# --- 유틸리티 함수 ---
def get_tokyo_time():
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    return datetime.datetime.now(tokyo_tz)


def calculate_work_hours(clock_in_str, clock_out_time):
    if not clock_out_time:
        return "근무 중"
    start_minutes = 9 * 60
    out_minutes = clock_out_time.hour * 60 + clock_out_time.minute
    if out_minutes <= start_minutes:
        return "0시간 0분"
    total_minutes = out_minutes - start_minutes
    lunch_start = 12 * 60
    lunch_end = 13 * 60
    if out_minutes >= lunch_end:
        total_minutes -= 60
    elif out_minutes > lunch_start:
        total_minutes -= out_minutes - lunch_start
    if total_minutes < 0:
        total_minutes = 0
    return f"{total_minutes // 60}시간 {total_minutes % 60}분"


def get_wh_stock(prod_code, wh_name):
    return st.session_state.warehouse_stocks.get(f"{prod_code}_{wh_name}", 0)


def update_wh_stock(prod_code, wh_name, qty_change):
    key = f"{prod_code}_{wh_name}"
    current = st.session_state.warehouse_stocks.get(key, 0)
    st.session_state.warehouse_stocks[key] = max(0, current + qty_change)


# ==========================================
# 3. 로그인 및 언어 설정
# ==========================================
st.sidebar.selectbox(
    "🌐 Language / 언어",
    ["한국어", "日本語", "English"],
    key="lang",
)
L = LANG_PACK[st.session_state.lang]

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
                    user = next(
                        (
                            u
                            for u in st.session_state.users
                            if u["id"] == input_id and u["pw"] == input_pw
                        ),
                        None,
                    )
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
                reg_position = st.selectbox("직급 *", POSITIONS)
                reg_role = st.selectbox("신청 권한 *", ROLES)

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

# ==========================================
# 4. 메인 ERP 애플리케이션
# ==========================================
else:
    user_id = st.session_state.logged_in_user["id"]
    user = next(u for u in st.session_state.users if u["id"] == user_id)
    st.session_state.logged_in_user = user

    user_role = user.get("role", "방문자")
    is_admin = user_role == "관리자" or user["id"] == "admin"
    is_visitor = user_role == "방문자"

    st.sidebar.write(f"**{L['user_info']}:** {user['name']} ({user['position']})")
    st.sidebar.write(f"**{L['role_info']}:** {user_role} {'👑' if is_admin else ''}")

    if st.sidebar.button(L["logout"], use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

    menu = st.sidebar.radio(
        L["menu"],
        [
            L["mypage"],
            L["dashboard"],
            L["attendance"],
            L["master_prod"],
            L["client_mgmt"],
            L["stock_mgmt"],
            L["stock_history"],
            L["sales_mgmt"],
            L["timecard"],
            L["sys_mgmt"],
        ],
    )

    tokyo_now = get_tokyo_time()
    st.info(f"🕒 **{L['tokyo_time']}:** {tokyo_now.strftime('%Y-%m-%d %H:%M:%S')} JST")

    # ------------------------------------------
    # 탭 0: 마이페이지
    # ------------------------------------------
    if menu == L["mypage"]:
        st.header(L["mypage"])
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📌 계정 정보")
            st.write(f"- **ID:** `{user['id']}`")
            st.write(f"- **Password:** `{user['pw']}`")
            st.write(f"- **Name:** {user['name']}")
            st.write(f"- **Position:** {user['position']}")
            st.write(f"- **Department:** {user['dept']}")
            st.write(f"- **Role:** {user['role']}")
        with c2:
            st.subheader("🌴 근태 및 휴가 정보")
            st.write(f"- **입사일:** {user.get('hire_date', '미등록')}")
            st.metric("잔여 휴가(연차) 일수", f"{user.get('annual_leave', 15.0):.1f} 일")

    # ------------------------------------------
    # 탭 1: 대시보드
    # ------------------------------------------
    elif menu == L["dashboard"]:
        st.header(L["dashboard"])
        total_items = len(st.session_state.master_products)
        total_qty = 0
        total_val = 0
        wh_summary = {wh: 0 for wh in WAREHOUSES}

        for p in st.session_state.master_products:
            p_code = p["code"]
            p_price = p["price"]
            for wh in WAREHOUSES:
                qty = get_wh_stock(p_code, wh)
                total_qty += qty
                total_val += qty * p_price
                wh_summary[wh] += qty

        m1, m2, m3 = st.columns(3)
        m1.metric("등록 상품 수", f"{total_items} 개")
        m2.metric("총 보유 재고량", f"{total_qty:,} 개")
        m3.metric("총 재고 금액 (매입가)", f"¥ {total_val:,}")

        st.markdown("---")
        st.subheader("🏢 창고별 재고 현황")
        cols = st.columns(len(WAREHOUSES))
        for idx, wh in enumerate(WAREHOUSES):
            cols[idx].info(f"**{wh}**\n\n### {wh_summary[wh]:,} 개")

        st.markdown("---")
        st.subheader("📦 상품별 보유 현황 (가로 통합 목록)")
        dash_data = []
        for p in st.session_state.master_products:
            p_code = p["code"]
            s_q = get_wh_stock(p_code, "SAGAWA")
            l_q = get_wh_stock(p_code, "L&K")
            d_q = get_wh_stock(p_code, "大吉商事")
            tot = s_q + l_q + d_q
            dash_data.append({
                "상품코드": p_code,
                "제품명": p["name"],
                "카테고리": p["category"],
                "매입단가": f"¥ {p['price']:,}",
                "SAGAWA": f"{s_q:,}",
                "L&K": f"{l_q:,}",
                "大吉商事": f"{d_q:,}",
                "총재고": f"{tot:,}",
                "총재고금액": f"¥ {tot * p['price']:,}",
            })
        st.dataframe(pd.DataFrame(dash_data), use_container_width=True)

    # ------------------------------------------
    # 탭 2: 출퇴근시스템
    # ------------------------------------------
    elif menu == L["attendance"]:
        st.header(L["attendance"])
        c1, c2 = st.columns(2)
        today_str = tokyo_now.strftime("%Y-%m-%d")
        record = next(
            (
                r
                for r in st.session_state.attendance_records
                if r["userId"] == user["id"] and r["date"] == today_str
            ),
            None,
        )

        with c1:
            st.subheader("☀️ 오늘 나의 출퇴근")
            st.write(f"- 오늘 날짜: {today_str}")
            st.write(f"- 출근 시각: {record['clockIn'] if record else '--:--:--'}")
            st.write(f"- 퇴근 시각: {record['clockOut'] if record else '--:--:--'}")
            st.write(f"- 실근무시간: {record['calculatedHoursStr'] if record else '0시간 0분'}")

            b1, b2 = st.columns(2)
            if b1.button("☀️ 출근", use_container_width=True, disabled=is_visitor):
                if record and record["clockIn"]:
                    st.warning("이미 출근 처리되었습니다.")
                else:
                    now_str = tokyo_now.strftime("%H:%M:%S")
                    st.session_state.attendance_records.append({
                        "date": today_str,
                        "userId": user["id"],
                        "userName": user["name"],
                        "clockIn": now_str,
                        "clockOut": "--:--:--",
                        "calculatedHoursStr": "근무 중",
                    })
                    st.success("출근 완료")
                    st.rerun()

            if b2.button("🌙 퇴근", use_container_width=True, disabled=is_visitor):
                if not record or not record["clockIn"]:
                    st.error("출근 기록이 없습니다.")
                else:
                    now_str = tokyo_now.strftime("%H:%M:%S")
                    record["clockOut"] = now_str
                    record["calculatedHoursStr"] = calculate_work_hours(
                        record["clockIn"], tokyo_now.time()
                    )
                    st.success("퇴근 완료")
                    st.rerun()

        with c2:
            st.subheader("📋 전체 출퇴근 기록")
            if st.session_state.attendance_records:
                st.dataframe(
                    pd.DataFrame(st.session_state.attendance_records),
                    use_container_width=True,
                )

    # ------------------------------------------
    # 탭 3: 마스터 상품 등록/관리 (가로형 배치 개편)
    # ------------------------------------------
    elif menu == L["master_prod"]:
        st.header(L["master_prod"])

        # 가로 배치형 등록 폼
        with st.expander("➕ 신규 마스터 상품 등록 (클릭하여 열기/접기)", expanded=True):
            with st.form("new_master_product_form"):
                r1_1, r1_2, r1_3, r1_4 = st.columns(4)
                p_code = r1_1.text_input("상품코드 * (예: PRD-1002)")
                p_name = r1_2.text_input("제품명 *")
                p_category = r1_3.text_input("카테고리 *", value="화장품/뷰티")
                p_price = r1_4.number_input("매입단가(엔) *", min_value=0, step=100)

                r2_1, r2_2, r2_3, r2_4 = st.columns(4)
                p_jan_pack = r2_1.text_input("JAN(곽)")
                p_jan_single = r2_2.text_input("JAN(낱장)")
                p_capacity = r2_3.text_input("용량")
                p_in_pack_qty = r2_4.text_input("입수량(곽/낱장)")

                r3_1, r3_2, r3_3, r3_4 = st.columns(4)
                p_prod_size = r3_1.text_input("제품사이즈(곽)")
                p_box_size = r3_2.text_input("박스사이즈(가*세*높)")
                p_plt_qty = r3_3.text_input("1 PLT 수량")
                p_vendor = r3_4.text_input("공급업체/제조사")

                if st.form_submit_button("마스터 상품 등록", disabled=is_visitor):
                    if not p_code or not p_name:
                        st.error("상품코드와 제품명은 필수입니다.")
                    elif any(p["code"] == p_code for p in st.session_state.master_products):
                        st.error("이미 등록된 상품코드입니다.")
                    else:
                        st.session_state.master_products.append({
                            "code": p_code,
                            "name": p_name,
                            "jan_pack": p_jan_pack,
                            "jan_single": p_jan_single,
                            "capacity": p_capacity,
                            "category": p_category,
                            "price": p_price,
                            "in_pack_qty": p_in_pack_qty,
                            "prod_size": p_prod_size,
                            "box_size": p_box_size,
                            "plt_qty": p_plt_qty,
                            "vendor": p_vendor,
                        })
                        st.success("등록 완료!")
                        st.rerun()

        st.markdown("---")
        st.subheader("📋 마스터 상품 목록 및 가로 즉시 수정")

        if st.session_state.master_products:
            df_m = pd.DataFrame(st.session_state.master_products)
            st.dataframe(df_m, use_container_width=True)

            # 가로 수정 섹션
            st.subheader("🛠️ 선택 상품 정보 저장 / 삭제")
            p_codes = [p["code"] for p in st.session_state.master_products]
            target_code = st.selectbox("수정할 상품 선택", p_codes)
            target_p = next(
                p for p in st.session_state.master_products if p["code"] == target_code
            )

            with st.form("edit_master_product_horizontal"):
                e1, e2, e3, e4, e5 = st.columns(5)
                e_name = e1.text_input("제품명", value=target_p["name"])
                e_cat = e2.text_input("카테고리", value=target_p["category"])
                e_price = e3.number_input(
                    "매입단가", min_value=0, value=int(target_p["price"])
                )
                e_jan_p = e4.text_input("JAN(곽)", value=target_p.get("jan_pack", ""))
                e_jan_s = e5.text_input("JAN(낱장)", value=target_p.get("jan_single", ""))

                btn_col1, btn_col2 = st.columns([1, 1])
                if btn_col1.form_submit_button("💾 수정사항 저장", disabled=is_visitor):
                    target_p["name"] = e_name
                    target_p["category"] = e_cat
                    target_p["price"] = e_price
                    target_p["jan_pack"] = e_jan_p
                    target_p["jan_single"] = e_jan_s
                    st.success("수정 저장이 완료되었습니다.")
                    st.rerun()

                if btn_col2.form_submit_button("❌ 선택 상품 삭제", disabled=not is_admin):
                    st.session_state.master_products.remove(target_p)
                    st.success("삭제되었습니다.")
                    st.rerun()

    # ------------------------------------------
    # 탭 4: 거래처 관리 (수정/삭제 제공)
    # ------------------------------------------
    elif menu == L["client_mgmt"]:
        st.header(L["client_mgmt"])

        tab1, tab2, tab3 = st.tabs(
            ["🏢 등록 거래처 & 상세 제품 조회", "➕ 신규 거래처 등록", "📦 거래처 제품 등록"]
        )

        with tab1:
            st.subheader("🏢 현재 등록된 거래처 목록")
            if st.session_state.clients:
                st.dataframe(
                    pd.DataFrame(st.session_state.clients), use_container_width=True
                )

                st.markdown("---")
                c_names = [c["name"] for c in st.session_state.clients]
                sel_c = st.selectbox("거래처 선택", c_names)
                target_c = next(
                    c for c in st.session_state.clients if c["name"] == sel_c
                )

                # 거래처 수정 / 삭제
                with st.expander(f"🛠️ [{sel_c}] 거래처 정보 수정 / 삭제"):
                    e_zip = st.text_input("우편번호", value=target_c.get("zipcode", ""))
                    e_addr = st.text_input("주소", value=target_c.get("address", ""))
                    e_phone = st.text_input("전화번호", value=target_c.get("phone", ""))

                    b_c1, b_c2 = st.columns(2)
                    if b_c1.button("거래처 저장", disabled=is_visitor):
                        target_c["zipcode"] = e_zip
                        target_c["address"] = e_addr
                        target_c["phone"] = e_phone
                        st.success("수정 완료")
                        st.rerun()
                    if b_c2.button("❌ 거래처 삭제", disabled=not is_admin):
                        st.session_state.clients.remove(target_c)
                        st.session_state.client_products = [
                            cp
                            for cp in st.session_state.client_products
                            if cp["client_name"] != sel_c
                        ]
                        st.success("삭제 완료")
                        st.rerun()

                st.subheader(f"📦 [{sel_c}] 등록된 거래 제품 목록")
                m_cps = [
                    cp
                    for cp in st.session_state.client_products
                    if cp["client_name"] == sel_c
                ]

                if m_cps:
                    st.dataframe(pd.DataFrame(m_cps), use_container_width=True)

                    with st.expander("🛠️ 거래 제품 수정 / 삭제"):
                        cp_names = [cp["prod_name"] for cp in m_cps]
                        sel_cp = st.selectbox("제품 선택", cp_names)
                        target_cp = next(
                            cp for cp in m_cps if cp["prod_name"] == sel_cp
                        )

                        e_cp_price = st.number_input(
                            "공급가(엔 vat-)",
                            min_value=0,
                            value=int(target_cp["supply_price"]),
                        )
                        e_cp_jan = st.text_input(
                            "JAN(곽)", value=target_cp.get("jan_pack", "")
                        )

                        cp1, cp2 = st.columns(2)
                        if cp1.button("제품 저장", disabled=is_visitor):
                            target_cp["supply_price"] = e_cp_price
                            target_cp["jan_pack"] = e_cp_jan
                            st.success("제품 정보 수정 완료")
                            st.rerun()
                        if cp2.button("❌ 제품 삭제", disabled=not is_admin):
                            st.session_state.client_products.remove(target_cp)
                            st.success("제품 삭제 완료")
                            st.rerun()
                else:
                    st.info("등록된 거래제품이 없습니다.")

        with tab2:
            st.subheader("➕ 신규 거래처 등록")
            with st.form("new_client_form"):
                nc_name = st.text_input("거래처명 *")
                nc_zip = st.text_input("우편번호 (예: 100-0001)")
                nc_addr = st.text_input("주소 *")
                nc_phone = st.text_input("전화번호 *")

                if st.form_submit_button("거래처 등록", disabled=is_visitor):
                    if not nc_name or not nc_addr:
                        st.error("필수 항목을 입력해 주세요.")
                    else:
                        st.session_state.clients.append({
                            "id": len(st.session_state.clients) + 1,
                            "name": nc_name,
                            "zipcode": nc_zip,
                            "address": nc_addr,
                            "phone": nc_phone,
                        })
                        st.success("등록 완료!")
                        st.rerun()

        with tab3:
            st.subheader("📦 거래처 제품 등록")
            if st.session_state.clients:
                c_names = [c["name"] for c in st.session_state.clients]
                target_c_p = st.selectbox("대상 거래처 선택", c_names)

                with st.form("new_client_prod_form"):
                    ncp_name = st.text_input("상품명 *")
                    ncp_jan_p = st.text_input("JAN(곽)")
                    ncp_jan_s = st.text_input("JAN(낱장)")
                    ncp_price = st.number_input(
                        "공급가(엔 VAT 별도) *", min_value=0, step=100
                    )

                    if st.form_submit_button("거래제품 등록", disabled=is_visitor):
                        if not ncp_name:
                            st.error("상품명은 필수입니다.")
                        else:
                            st.session_state.client_products.append({
                                "client_name": target_c_p,
                                "prod_name": ncp_name,
                                "jan_pack": ncp_jan_p,
                                "jan_single": ncp_jan_s,
                                "supply_price": ncp_price,
                            })
                            st.success("등록 완료!")
                            st.rerun()

    # ------------------------------------------
    # 탭 5: 재고관리 (입고/출고)
    # ------------------------------------------
    elif menu == L["stock_mgmt"]:
        st.header(L["stock_mgmt"])

        mode = st.radio("작업 선택", ["📥 입고 등록", "📤 출고 등록 (우편번호 포함)"])

        if mode == "📥 입고 등록":
            st.subheader("📥 입고 등록")
            if st.session_state.master_products:
                prod_map = {
                    f"[{p['code']}] {p['name']}": p
                    for p in st.session_state.master_products
                }
                sel_p_label = st.selectbox("상품 선택", list(prod_map.keys()))
                sel_p = prod_map[sel_p_label]

                with st.form("inbound_form"):
                    in_wh = st.selectbox("입고 창고 *", WAREHOUSES)
                    in_jan = st.text_input("JAN 코드", value=sel_p.get("jan_pack", ""))
                    in_price = st.number_input(
                        "매입단가(엔)", min_value=0, value=int(sel_p["price"])
                    )
                    in_qty = st.number_input("입고 수량", min_value=1, value=10)

                    if st.form_submit_button("입고 완료", disabled=is_visitor):
                        update_wh_stock(sel_p["code"], in_wh, in_qty)
                        po_code = f"IN-{tokyo_now.strftime('%Y%m%d%H%M%S')}"
                        st.session_state.stock_logs.append({
                            "po_no": po_code,
                            "date": tokyo_now.strftime("%Y-%m-%d"),
                            "type": "입고",
                            "wh": in_wh,
                            "client": "-",
                            "prod_name": sel_p["name"],
                            "jan": in_jan,
                            "qty": in_qty,
                            "unit_price": in_price,
                            "total_price": in_price * in_qty,
                            "trade_type": "매입",
                            "manager": user["name"],
                            "zipcode": "-",
                            "ship_to": "-",
                        })
                        st.success("입고 처리가 완료되었습니다.")
                        st.rerun()

        else:
            st.subheader("📤 출고 등록 (우편번호 항목 반영)")
            if st.session_state.clients:
                c_names = [c["name"] for c in st.session_state.clients]
                sel_c_name = st.selectbox("1. 거래처 선택", c_names)
                sel_c_obj = next(
                    c for c in st.session_state.clients if c["name"] == sel_c_name
                )
                avail_cps = [
                    cp
                    for cp in st.session_state.client_products
                    if cp["client_name"] == sel_c_name
                ]

                if avail_cps:
                    st.markdown("---")
                    st.subheader("2. Delivery & Ship-to Information (우편번호 포함)")

                    c_a, c_b = st.columns(2)
                    out_wh = c_a.selectbox("출고 창고 *", WAREHOUSES)
                    ship_name = c_a.text_input("납품처명 *", value=sel_c_name)
                    ship_zip = c_b.text_input(
                        "우편번호 *", value=sel_c_obj.get("zipcode", "")
                    )
                    ship_addr = c_b.text_input("주소 *", value=sel_c_obj["address"])
                    ship_phone = c_a.text_input("전화번호 *", value=sel_c_obj["phone"])

                    st.markdown("---")
                    st.subheader("3. 출고 대상 제품 선택")
                    num_items = st.number_input(
                        "품목 개수", min_value=1, max_value=30, value=1
                    )
                    cp_labels = [f"{cp['prod_name']} (¥{cp['supply_price']:,})" for cp in avail_cps]

                    with st.form("multi_outbound_form"):
                        items_out = []
                        po_code = f"OUT-{tokyo_now.strftime('%Y%m%d%H%M%S')}"

                        for i in range(int(num_items)):
                            col1, col2, col3 = st.columns([3, 2, 2])
                            idx = col1.selectbox(
                                f"제품 #{i+1}",
                                range(len(cp_labels)),
                                format_func=lambda x: cp_labels[x],
                                key=f"o_cp_{i}",
                            )
                            t_type = col2.selectbox(
                                f"거래방식 #{i+1}",
                                ["납품", "FOC", "테스터"],
                                key=f"o_tr_{i}",
                            )
                            q_val = col3.number_input(
                                f"수량 #{i+1}", min_value=1, value=1, key=f"o_q_{i}"
                            )

                            cp_item = avail_cps[idx]
                            u_price = 0 if t_type in ["FOC", "테스터"] else cp_item["supply_price"]
                            items_out.append({
                                "cp": cp_item,
                                "trade_type": t_type,
                                "qty": q_val,
                                "unit_price": u_price,
                                "total": u_price * q_val,
                            })

                        if st.form_submit_button("일괄 출고 실행", disabled=is_visitor):
                            for it in items_out:
                                cp_o = it["cp"]
                                matched_m = next(
                                    (
                                        m
                                        for m in st.session_state.master_products
                                        if m["name"] == cp_o["prod_name"]
                                    ),
                                    None,
                                )
                                if matched_m:
                                    update_wh_stock(matched_m["code"], out_wh, -it["qty"])

                                st.session_state.stock_logs.append({
                                    "po_no": po_code,
                                    "date": tokyo_now.strftime("%Y-%m-%d"),
                                    "type": "출고",
                                    "wh": out_wh,
                                    "client": sel_c_name,
                                    "prod_name": cp_o["prod_name"],
                                    "jan": cp_o.get("jan_pack", ""),
                                    "qty": it["qty"],
                                    "unit_price": it["unit_price"],
                                    "total_price": it["total"],
                                    "trade_type": it["trade_type"],
                                    "manager": user["name"],
                                    "zipcode": ship_zip,
                                    "ship_to": f"{ship_name} / {ship_addr} / {ship_phone}",
                                })
                            st.success("출고 완료되었습니다.")
                            st.rerun()

    # ------------------------------------------
    # 탭 6: 입출고 이력 조회 (독립 메뉴 & 다중 필터)
    # ------------------------------------------
    elif menu == L["stock_history"]:
        st.header("📜 입출고 이력 통합 조회")

        # 가로 다중 필터
        f1, f2, f3, f4 = st.columns([2, 2, 3, 3])

        all_clients = ["전체"] + [c["name"] for c in st.session_state.clients]
        filter_c = f1.selectbox("거래처 선택", all_clients)

        all_whs = ["전체"] + WAREHOUSES
        filter_wh = f2.selectbox("창고 선택", all_whs)

        start_d = f3.date_input(
            "시작일", datetime.date.today() - datetime.timedelta(days=30)
        )
        end_d = f3.date_input("종료일", datetime.date.today())

        search_kw = f4.text_input("검색어 (상품명 / 바코드 / 발주번호)")

        logs = st.session_state.stock_logs

        # 필터링 적용
        filtered_logs = []
        for l in logs:
            l_date = datetime.datetime.strptime(l["date"], "%Y-%m-%d").date()
            if not (start_d <= l_date <= end_d):
                continue
            if filter_c != "전체" and l["client"] != filter_c:
                continue
            if filter_wh != "전체" and l["wh"] != filter_wh:
                continue
            if search_kw:
                kw = search_kw.lower()
                if (
                    kw not in l["prod_name"].lower()
                    and kw not in l.get("jan", "").lower()
                    and kw not in l.get("po_no", "").lower()
                ):
                    continue
            filtered_logs.append(l)

        st.markdown("---")
        st.write(f"**총 {len(filtered_logs)} 건의 입출고 내역이 검색되었습니다.**")

        if filtered_logs:
            df_hist = pd.DataFrame(filtered_logs)[
                [
                    "po_no",
                    "date",
                    "type",
                    "wh",
                    "client",
                    "prod_name",
                    "jan",
                    "qty",
                    "unit_price",
                    "total_price",
                    "trade_type",
                    "zipcode",
                    "ship_to",
                    "manager",
                ]
            ]
            df_hist.columns = [
                "발주/입출고번호",
                "날짜",
                "구분",
                "창고",
                "거래처",
                "상품명",
                "JAN/바코드",
                "수량",
                "단가(엔)",
                "총금액(엔)",
                "거래방식",
                "우편번호",
                "배송지정보",
                "담당자",
            ]
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("조건에 일치하는 이력이 없습니다.")

    # ------------------------------------------
    # 탭 7: 매출 관리 (독립 메뉴 & 다중 필터)
    # ------------------------------------------
    elif menu == L["sales_mgmt"]:
        st.header("💰 매출 관리 (납품일/출고건 기준)")

        # 가로 다중 필터
        sf1, sf2, sf3, sf4 = st.columns([2, 2, 3, 3])

        all_c_s = ["전체"] + [c["name"] for c in st.session_state.clients]
        s_filter_c = sf1.selectbox("거래처 선택 ", all_c_s)

        all_w_s = ["전체"] + WAREHOUSES
        s_filter_wh = sf2.selectbox("창고 선택 ", all_w_s)

        s_start_d = sf3.date_input(
            "시작일 ", datetime.date.today() - datetime.timedelta(days=30)
        )
        s_end_d = sf3.date_input("종료일 ", datetime.date.today())

        s_kw = sf4.text_input("검색어 (상품명 / 바코드 / 발주번호) ")

        # 출고건만 매출 집계 대상으로 추출
        sales_data = []
        for l in st.session_state.stock_logs:
            if l["type"] != "출고":
                continue
            l_date = datetime.datetime.strptime(l["date"], "%Y-%m-%d").date()
            if not (s_start_d <= l_date <= s_end_d):
                continue
            if s_filter_c != "전체" and l["client"] != s_filter_c:
                continue
            if s_filter_wh != "전체" and l["wh"] != s_filter_wh:
                continue
            if s_kw:
                kw = s_kw.lower()
                if (
                    kw not in l["prod_name"].lower()
                    and kw not in l.get("jan", "").lower()
                    and kw not in l.get("po_no", "").lower()
                ):
                    continue

            sales_data.append({
                "발주번호": l.get("po_no", "-"),
                "납품일(출고일)": l["date"],
                "거래처명": l["client"],
                "출고창고": l["wh"],
                "제품명": l["prod_name"],
                "JAN/바코드": l.get("jan", "-"),
                "발주량(수량)": l["qty"],
                "공급가(엔 VAT-)": l["unit_price"],
                "총매출액(공급가*발주량)": l["total_price"],
                "거래방식": l["trade_type"],
            })

        st.markdown("---")
        total_sales_sum = sum(item["총매출액(공급가*발주량)"] for item in sales_data)
        st.metric("📊 조회 기간 총 매출액", f"¥ {total_sales_sum:,}")

        if sales_data:
            st.dataframe(pd.DataFrame(sales_data), use_container_width=True)
        else:
            st.info("조건에 부합하는 매출 데이터가 없습니다.")

    # ------------------------------------------
    # 탭 8: 타임카드 (일본 기준 캘린더 & 수정/삭제)
    # ------------------------------------------
    elif menu == L["timecard"]:
        st.header("📆 타임카드 (일본 기준 캘린더 & 일정 관리)")

        c1, c2 = st.columns([1, 1])

        with c1:
            st.subheader("📝 휴가 / 일정 신청")
            with st.form("leave_request_form"):
                l_type = st.selectbox("신청 유형", ["연차", "반차", "병가", "경조사", "출장"])
                l_start = st.date_input("시작일")
                l_end = st.date_input("종료일")
                l_reason = st.text_area("사유")

                if st.form_submit_button("신청 제출", disabled=is_visitor):
                    st.session_state.leave_records.append({
                        "applicant": user["name"],
                        "type": l_type,
                        "start_date": str(l_start),
                        "end_date": str(l_end),
                        "reason": l_reason,
                        "status": "승인 대기",
                    })
                    st.success("신청 완료!")
                    st.rerun()

            st.subheader("📋 신청 및 결재 현황")
            if is_admin and st.session_state.leave_records:
                with st.expander("👑 [관리자] 휴가 승인/반려"):
                    idx_l = st.selectbox(
                        "항목 선택", range(len(st.session_state.leave_records))
                    )
                    b_a, b_r = st.columns(2)
                    if b_a.button("✅ 승인"):
                        st.session_state.leave_records[idx_l]["status"] = "승인 완료"
                        st.success("승인 처리되었습니다.")
                        st.rerun()
                    if b_r.button("❌ 반려"):
                        st.session_state.leave_records[idx_l]["status"] = "반려"
                        st.error("반려 처리되었습니다.")
                        st.rerun()

            if st.session_state.leave_records:
                st.dataframe(
                    pd.DataFrame(st.session_state.leave_records),
                    use_container_width=True,
                )

        with c2:
            st.subheader("🇯🇵 일본 기준 월별 캘린더 & 휴무일 관리")

            # 관리자 전용 휴무일 등록/수정/삭제
            if is_admin:
                with st.expander("👑 [관리자] 일본 공휴일/회사 휴무일 등록·수정·삭제"):
                    tab_h1, tab_h2 = st.tabs(["➕ 휴무일 등록", "🛠️ 휴무일 수정/삭제"])

                    with tab_h1:
                        with st.form("add_holiday_form"):
                            hd_date = st.date_input("날짜")
                            hd_title = st.text_input("휴무일 명칭 (예: 夏休み)")
                            hd_type = st.selectbox(
                                "구분", ["일본 공휴일", "회사 휴무", "전체 월차"]
                            )

                            if st.form_submit_button("휴무일 추가"):
                                new_h_id = len(st.session_state.company_holidays) + 1
                                st.session_state.company_holidays.append({
                                    "id": new_h_id,
                                    "date": str(hd_date),
                                    "title": hd_title,
                                    "type": hd_type,
                                })
                                st.success("휴무일이 등록되었습니다.")
                                st.rerun()

                    with tab_h2:
                        if st.session_state.company_holidays:
                            h_options = [
                                f"[{h['date']}] {h['title']}"
                                for h in st.session_state.company_holidays
                            ]
                            sel_h_opt = st.selectbox("수정/삭제할 휴무일 선택", h_options)
                            sel_h_idx = h_options.index(sel_h_opt)
                            target_h = st.session_state.company_holidays[sel_h_idx]

                            e_h_title = st.text_input("휴무명 수정", value=target_h["title"])
                            e_h_type = st.selectbox(
                                "구분 수정",
                                ["일본 공휴일", "회사 휴무", "전체 월차"],
                                index=["일본 공휴일", "회사 휴무", "전체 월차"].index(
                                    target_h.get("type", "일본 공휴일")
                                ),
                            )

                            hb1, hb2 = st.columns(2)
                            if hb1.button("휴무일 저장"):
                                target_h["title"] = e_h_title
                                target_h["type"] = e_h_type
                                st.success("수정 완료")
                                st.rerun()

                            if hb2.button("❌ 휴무일 삭제"):
                                del st.session_state.company_holidays[sel_h_idx]
                                st.success("삭제 완료")
                                st.rerun()

            cy_col, cm_col = st.columns(2)
            sel_y = cy_col.number_input(
                "연도", min_value=2020, max_value=2030, value=tokyo_now.year
            )
            sel_m = cm_col.number_input(
                "월", min_value=1, max_value=12, value=tokyo_now.month
            )

            st.write(f"### 📅 {sel_y}年 {sel_m}月 Calendar")
            cal = calendar.monthcalendar(int(sel_y), int(sel_m))
            st.dataframe(
                pd.DataFrame(cal, columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
                use_container_width=True,
            )

            st.markdown("**📍 이 달의 일본 공휴일 및 회사 휴무:**")
            m_prefix = f"{sel_y}-{int(sel_m):02d}"

            for h in st.session_state.company_holidays:
                if h["date"].startswith(m_prefix):
                    st.write(f"🔴 **[{h['date']}]** {h['title']} ({h['type']})")

    # ------------------------------------------
    # 탭 9: 시스템 관리
    # ------------------------------------------
    elif menu == L["sys_mgmt"]:
        st.header(L["sys_mgmt"])

        t_u1, t_u2 = st.tabs(["👥 전체 계정 수정/관리", "👔 직원 정보 관리"])

        with t_u1:
            if is_admin:
                st.subheader("👑 계정 수정 및 승인 관리")
                u_ids = [u["id"] for u in st.session_state.users]
                sel_u = st.selectbox("수정할 계정 선택", u_ids)
                t_user = next(u for u in st.session_state.users if u["id"] == sel_u)

                with st.form("edit_user_form"):
                    eu_name = st.text_input("이름", value=t_user["name"])
                    eu_pos = st.selectbox("직급", POSITIONS)
                    eu_dept = st.text_input("부서", value=t_user.get("dept", ""))
                    eu_role = st.selectbox("권한", ROLES)
                    eu_status = st.selectbox(
                        "상태", ["승인 완료", "승인 대기"]
                    )

                    if st.form_submit_button("계정 저장"):
                        t_user["name"] = eu_name
                        t_user["position"] = eu_pos
                        t_user["dept"] = eu_dept
                        t_user["role"] = eu_role
                        t_user["status"] = eu_status
                        st.success("수정 저장이 완료되었습니다.")
                        st.rerun()

            st.markdown("---")
            st.subheader("📋 등록 계정 현황")
            st.dataframe(
                pd.DataFrame(st.session_state.users)[
                    [
                        "id",
                        "name",
                        "position",
                        "dept",
                        "role",
                        "status",
                        "hire_date",
                        "annual_leave",
                    ]
                ],
                use_container_width=True,
            )

        with t_u2:
            st.subheader("👔 직원 인사 정보 관리 (입사일/잔여연차)")
            if is_admin:
                e_ids = [u["id"] for u in st.session_state.users]
                s_e_id = st.selectbox("직원 선택", e_ids)
                t_e = next(u for u in st.session_state.users if u["id"] == s_e_id)

                with st.form("emp_mgmt_form"):
                    e_hire = st.date_input(
                        "입사일",
                        value=datetime.datetime.strptime(
                            t_e.get("hire_date", str(datetime.date.today())), "%Y-%m-%d"
                        ).date(),
                    )
                    e_leave = st.number_input(
                        "잔여 연차",
                        min_value=0.0,
                        max_value=50.0,
                        value=float(t_e.get("annual_leave", 15.0)),
                        step=0.5,
                    )

                    if st.form_submit_button("인사정보 저장"):
                        t_e["hire_date"] = str(e_hire)
                        t_e["annual_leave"] = e_leave
                        st.success("저장되었습니다.")
                        st.rerun()

            st.markdown("---")
            st.dataframe(
                pd.DataFrame(st.session_state.users)[
                    ["id", "name", "position", "dept", "hire_date", "annual_leave"]
                ],
                use_container_width=True,
            )
