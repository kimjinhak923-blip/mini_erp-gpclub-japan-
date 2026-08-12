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
# 1. 세션 상태(데이터베이스) 초기화
# ==========================================
# 1-1. 사용자 계정 (기본 admin + 입사일/잔여연차 관리)
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

# 1-2. 기본 카테고리
if "categories" not in st.session_state:
    st.session_state.categories = ["전자기기", "사무용품", "소모품", "가구/집기", "화장품/뷰티"]

# 1-3. 마스터 상품 데이터 (요청된 규격 반영)
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
            "origin": "한국",
            "desc": "기본 마스크팩",
        }
    ]

# 1-4. 창고별 재고 데이터
if "warehouse_stocks" not in st.session_state:
    st.session_state.warehouse_stocks = {
        "PRD-1001_SAGAWA": 50,
        "PRD-1001_L&K": 30,
        "PRD-1001_大吉商事": 20,
    }

# 1-5. 거래처 및 거래처별 거래제품 데이터
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
            "capacity": "10매/곽",
            "category": "화장품/뷰티",
            "supply_price": 4500,  # 엔화 VAT 별도
        }
    ]

# 1-6. 입출고 이력 데이터
if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = []

# 1-7. 근태, 타임카드, 회사 전체 휴무일/일정 데이터
if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = []

if "leave_records" not in st.session_state:
    st.session_state.leave_records = []

if "company_holidays" not in st.session_state:
    st.session_state.company_holidays = [
        {"date": "2026-08-15", "title": "광복절/휴무일", "type": "회사휴무"}
    ]


# --- 유틸리티 함수 ---
def get_tokyo_time():
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    return datetime.datetime.now(tokyo_tz)


def calculate_work_hours(clock_in_str, clock_out_time):
    if not clock_out_time:
        return "근무 중"

    start_minutes = 9 * 60  # 09:00 고정
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

    work_h = total_minutes // 60
    work_m = total_minutes % 60
    return f"{work_h}시간 {work_m}분"


def get_wh_stock(prod_code, wh_name):
    key = f"{prod_code}_{wh_name}"
    return st.session_state.warehouse_stocks.get(key, 0)


def update_wh_stock(prod_code, wh_name, qty_change):
    key = f"{prod_code}_{wh_name}"
    current = st.session_state.warehouse_stocks.get(key, 0)
    st.session_state.warehouse_stocks[key] = max(0, current + qty_change)


# ==========================================
# 2. 로그인 및 계정 신청 화면
# ==========================================
if st.session_state.logged_in_user is None:
    st.title("🔒 사내 통합 관리 시스템")

    tab_login, tab_register = st.tabs(["🔑 로그인", "📝 계정 생성 신청"])

    with tab_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                input_id = st.text_input("아이디")
                input_pw = st.text_input("비밀번호", type="password")
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
                            st.warning("계정 승인 대기 중입니다. 관리자에게 문의하세요.")
                        else:
                            st.session_state.logged_in_user = user
                            st.success(f"{user['name']}님 환영합니다!")
                            st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

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

                reg_submit = st.form_submit_button("계정 신청 제출", use_container_width=True)

                if reg_submit:
                    if not reg_id or not reg_pw or not reg_name:
                        st.error("필수 항목(*)을 모두 입력해주세요.")
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
                        st.success("계정 신청이 완료되었습니다! (관리자 승인 후 로그인 가능)")

# ==========================================
# 3. 메인 ERP 시스템 애플리케이션
# ==========================================
else:
    # 세션 유저 객체 갱신
    user_id = st.session_state.logged_in_user["id"]
    user = next(u for u in st.session_state.users if u["id"] == user_id)
    st.session_state.logged_in_user = user

    user_role = user.get("role", "방문자")
    is_admin = user_role == "관리자" or user["id"] == "admin"
    is_staff = user_role == "STAFF"
    is_visitor = user_role == "방문자"

    # 사이드바
    st.sidebar.title("🏢 WORK MANAGER")
    st.sidebar.write(f"**접속자:** {user['name']} ({user['position']})")
    st.sidebar.write(f"**권한:** {user_role} {'👑' if is_admin else ''}")

    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

    menu = st.sidebar.radio(
        "메뉴 이동",
        [
            "👤 마이페이지",
            "대시보드",
            "출퇴근시스템(현황)",
            "마스터 상품 등록/관리",
            "거래처 관리",
            "재고관리 (입고/출고)",
            "타임카드 (휴가/일정)",
            "시스템 관리 (사용자/권한)",
        ],
    )

    tokyo_now = get_tokyo_time()
    st.info(f"🕒 **도쿄 기준 시간 (Asia/Tokyo):** {tokyo_now.strftime('%Y-%m-%d %H:%M:%S')} JST")

    # ------------------------------------------
    # 탭 0: 마이페이지
    # ------------------------------------------
    if menu == "👤 마이페이지":
        st.header("👤 마이페이지 (My Page)")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📌 내 계정 프로필 정보")
            st.write(f"- **아이디 (ID):** `{user['id']}`")
            st.write(f"- **비밀번호 (PW):** `{user['pw']}`")
            st.write(f"- **성명:** {user['name']}")
            st.write(f"- **직급:** {user['position']}")
            st.write(f"- **소속 부서:** {user['dept']}")
            st.write(f"- **계정 권한:** {user['role']}")

        with col2:
            st.subheader("🌴 휴가 및 근태 요약")
            st.write(f"- **입사일:** {user.get('hire_date', '미등록')}")
            st.metric("현재 잔여 휴가(연차) 일수", f"{user.get('annual_leave', 15.0):.1f} 일")
            st.caption("※ 잔여 연차 수정은 시스템 관리자에게 문의 바랍니다.")

    # ------------------------------------------
    # 탭 1: 대시보드
    # ------------------------------------------
    elif menu == "대시보드":
        st.header("📊 재고 및 보유 현황 대시보드")

        total_items_type = len(st.session_state.master_products)
        total_stock_qty = 0
        total_stock_val = 0
        wh_summary = {wh: 0 for wh in WAREHOUSES}

        for p in st.session_state.master_products:
            p_code = p["code"]
            p_price = p["price"]
            for wh in WAREHOUSES:
                qty = get_wh_stock(p_code, wh)
                total_stock_qty += qty
                total_stock_val += qty * p_price
                wh_summary[wh] += qty

        m1, m2, m3 = st.columns(3)
        m1.metric("등록 상품 수", f"{total_items_type} 개")
        m2.metric("총 보유 재고량", f"{total_stock_qty:,} 개")
        m3.metric("보유재고 총 금액 (매입가 기준)", f"¥ {total_stock_val:,}")

        st.markdown("---")

        st.subheader("🏢 창고별 재고 수량 현황")
        w_cols = st.columns(len(WAREHOUSES))
        for idx, wh in enumerate(WAREHOUSES):
            with w_cols[idx]:
                st.info(f"**{wh}**\n\n### {wh_summary[wh]:,} 개")

        st.markdown("---")

        st.subheader("📦 상품별 잔여 재고 및 창고별 보유 현황")
        dash_data = []
        for p in st.session_state.master_products:
            p_code = p["code"]
            sag_q = get_wh_stock(p_code, "SAGAWA")
            lnk_q = get_wh_stock(p_code, "L&K")
            daik_q = get_wh_stock(p_code, "大吉商事")
            tot_q = sag_q + lnk_q + daik_q
            tot_val = tot_q * p["price"]

            dash_data.append({
                "상품코드": p_code,
                "상품명": p["name"],
                "카테고리": p["category"],
                "매입단가(엔)": f"¥ {p['price']:,}",
                "SAGAWA 재고": f"{sag_q:,}",
                "L&K 재고": f"{lnk_q:,}",
                "大吉商事 재고": f"{daik_q:,}",
                "총 잔여수량": f"{tot_q:,}",
                "총 매입금액": f"¥ {tot_val:,}",
            })

        if dash_data:
            st.dataframe(pd.DataFrame(dash_data), use_container_width=True)
        else:
            st.info("등록된 마스터 상품이 없습니다.")

    # ------------------------------------------
    # 탭 2: 출퇴근시스템(현황)
    # ------------------------------------------
    elif menu == "출퇴근시스템(현황)":
        st.header("⏱️ 출퇴근시스템 (현황 및 기록)")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("☀️ 오늘 나의 출퇴근 등록")
            today_str = tokyo_now.strftime("%Y-%m-%d")
            record = next(
                (
                    r
                    for r in st.session_state.attendance_records
                    if r["userId"] == user["id"] and r["date"] == today_str
                ),
                None,
            )

            clock_in_disp = record["clockIn"] if record else "--:--:--"
            clock_out_disp = record["clockOut"] if record else "--:--:--"
            work_hours_disp = record["calculatedHoursStr"] if record else "0시간 0분"

            st.write(f"- **오늘 날짜:** {today_str}")
            st.write(f"- **출근 기록 시각:** {clock_in_disp}")
            st.write(f"- **퇴근 기록 시각:** {clock_out_disp}")
            st.write(f"- **인정 실근무시간:** {work_hours_disp}")

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("☀️ 출근하기", use_container_width=True, disabled=is_visitor):
                    now_time_str = tokyo_now.strftime("%H:%M:%S")
                    if record and record["clockIn"]:
                        st.warning("이미 출근 기록이 존재합니다.")
                    else:
                        st.session_state.attendance_records.append({
                            "date": today_str,
                            "userId": user["id"],
                            "userName": user["name"],
                            "clockIn": now_time_str,
                            "clockOut": "--:--:--",
                            "calculatedHoursStr": "근무 중",
                        })
                        st.success(f"출근 처리되었습니다. ({now_time_str})")
                        st.rerun()

            with btn2:
                if st.button("🌙 퇴근하기", use_container_width=True, disabled=is_visitor):
                    now_time = tokyo_now.time()
                    now_time_str = tokyo_now.strftime("%H:%M:%S")
                    if not record or not record["clockIn"]:
                        st.error("출근 기록이 존재하지 않습니다.")
                    else:
                        record["clockOut"] = now_time_str
                        record["calculatedHoursStr"] = calculate_work_hours(
                            record["clockIn"], now_time
                        )
                        st.success(f"퇴근 처리되었습니다. ({now_time_str})")
                        st.rerun()

        with col2:
            st.subheader("📋 전체 출퇴근 기록 현황")
            if is_admin and st.session_state.attendance_records:
                with st.expander("👑 [관리자 전용] 출퇴근 기록 삭제"):
                    del_idx = st.number_input(
                        "삭제할 행 번호",
                        min_value=0,
                        max_value=len(st.session_state.attendance_records) - 1,
                        step=1,
                    )
                    if st.button("기록 삭제"):
                        del st.session_state.attendance_records[del_idx]
                        st.success("삭제되었습니다.")
                        st.rerun()

            if st.session_state.attendance_records:
                df_att = pd.DataFrame(st.session_state.attendance_records)
                df_att.columns = ["날짜", "사용자ID", "성명", "출근시각", "퇴근시각", "인정근무시간"]
                st.dataframe(df_att, use_container_width=True)
            else:
                st.info("출퇴근 기록이 없습니다.")

    # ------------------------------------------
    # 탭 3: 마스터 상품 등록/관리 (간소화 & 규격 반영)
    # ------------------------------------------
    elif menu == "마스터 상품 등록/관리":
        st.header("📦 마스터 상품 기본 정보 등록/관리")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("신규 마스터 상품 등록")
            with st.form("product_form"):
                p_code = st.text_input("상품 코드 * (예: PRD-1002)")
                p_name = st.text_input("제품명 *")
                p_jan_pack = st.text_input("JAN 코드 (곽)")
                p_jan_single = st.text_input("JAN 코드 (낱장)")
                p_capacity = st.text_input("용량 (예: 500ml, 10매/곽)")
                p_category = st.text_input("제품 카테고리 (직접 입력) *", value="화장품/뷰티")
                p_price = st.number_input("매입단가(엔/원) *", min_value=0, step=100)
                p_in_pack_qty = st.text_input("입수량 (곽/낱장) (예: 1곽 10장)")
                p_prod_size = st.text_input("제품 사이즈 (곽) (예: 10x15x2 cm)")
                p_box_size = st.text_input("박스 사이즈 (가로*세로*높이)")
                p_plt_qty = st.text_input("1 PLT 수량 (곽/박스)")
                p_vendor = st.text_input("공급업체 / 제조사")

                p_submit = st.form_submit_button("마스터 상품 등록", disabled=is_visitor)

                if p_submit:
                    if not p_code or not p_name:
                        st.error("상품 코드와 제품명은 필수 입력 항목입니다.")
                    elif any(p["code"] == p_code for p in st.session_state.master_products):
                        st.error("이미 존재하는 상품 코드입니다.")
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
                        st.success(f"상품 [{p_name}] 등록 완료!")
                        st.rerun()

        with col2:
            st.subheader("등록된 마스터 상품 수정 / 삭제")

            if st.session_state.master_products:
                prod_labels = [
                    f"[{p['code']}] {p['name']}" for p in st.session_state.master_products
                ]
                sel_prod_label = st.selectbox("수정/삭제할 상품 선택", prod_labels)
                sel_idx = prod_labels.index(sel_prod_label)
                target_prod = st.session_state.master_products[sel_idx]

                with st.expander("🛠️ 선택한 상품 정보 수정 및 삭제", expanded=True):
                    edit_name = st.text_input("제품명 수정", value=target_prod.get("name", ""))
                    edit_cat = st.text_input("카테고리 수정", value=target_prod.get("category", ""))
                    edit_price = st.number_input(
                        "매입단가 수정", min_value=0, value=int(target_prod.get("price", 0))
                    )
                    edit_jan_p = st.text_input("JAN(곽) 수정", value=target_prod.get("jan_pack", ""))
                    edit_jan_s = st.text_input("JAN(낱장) 수정", value=target_prod.get("jan_single", ""))

                    btn_e1, btn_e2 = st.columns(2)
                    with btn_e1:
                        if st.button("수정사항 저장", disabled=is_visitor):
                            target_prod["name"] = edit_name
                            target_prod["category"] = edit_cat
                            target_prod["price"] = edit_price
                            target_prod["jan_pack"] = edit_jan_p
                            target_prod["jan_single"] = edit_jan_s
                            st.success("상품 정보가 수정되었습니다.")
                            st.rerun()
                    with btn_e2:
                        if st.button("❌ 상품 삭제", disabled=not is_admin):
                            del st.session_state.master_products[sel_idx]
                            st.success("상품이 삭제되었습니다.")
                            st.rerun()

                st.markdown("---")
                df_prod = pd.DataFrame(st.session_state.master_products)
                st.dataframe(df_prod, use_container_width=True)
            else:
                st.info("등록된 상품이 없습니다.")

    # ------------------------------------------
    # 탭 4: 거래처 관리 (메인 목록 및 상세 거래제품 연동)
    # ------------------------------------------
    elif menu == "거래처 관리":
        st.header("🤝 거래처 및 거래제품 종합 관리")

        tab_c_list, tab_c_reg, tab_cp_reg = st.tabs(
            ["🏢 등록 거래처 및 상세 제품 조회", "➕ 신규 거래처 등록", "📦 거래처 제품 등록"]
        )

        # 1. 거래처 목록 및 상세 제품 보기 / 수정 / 삭제
        with tab_c_list:
            st.subheader("🏢 현재 등록된 거래처 목록")

            if st.session_state.clients:
                df_clients = pd.DataFrame(st.session_state.clients)
                st.dataframe(df_clients, use_container_width=True)

                st.markdown("---")
                st.subheader("🔍 거래처 상세 선택 (거래 제품 확인 및 관리)")

                client_names = [c["name"] for c in st.session_state.clients]
                selected_c_name = st.selectbox("조회/수정할 거래처 선택", client_names)

                target_c = next(c for c in st.session_state.clients if c["name"] == selected_c_name)

                # 거래처 수정 및 삭제
                with st.expander(f"🛠️ [{selected_c_name}] 거래처 정보 수정 / 삭제"):
                    edit_c_zip = st.text_input("우편번호 수정", value=target_c.get("zipcode", ""))
                    edit_c_addr = st.text_input("주소 수정", value=target_c.get("address", ""))
                    edit_c_phone = st.text_input("전화번호 수정", value=target_c.get("phone", ""))

                    ec1, ec2 = st.columns(2)
                    if ec1.button("거래처 정보 수정 저장", disabled=is_visitor):
                        target_c["zipcode"] = edit_c_zip
                        target_c["address"] = edit_c_addr
                        target_c["phone"] = edit_c_phone
                        st.success("거래처 정보가 수정되었습니다.")
                        st.rerun()

                    if ec2.button("❌ 거래처 삭제", disabled=not is_admin):
                        st.session_state.clients = [
                            c for c in st.session_state.clients if c["name"] != selected_c_name
                        ]
                        st.session_state.client_products = [
                            cp
                            for cp in st.session_state.client_products
                            if cp["client_name"] != selected_c_name
                        ]
                        st.success("거래처 및 연관 거래제품이 삭제되었습니다.")
                        st.rerun()

                st.subheader(f"📦 [{selected_c_name}] 거래 제품 목록")
                matched_cps = [
                    cp
                    for cp in st.session_state.client_products
                    if cp["client_name"] == selected_c_name
                ]

                if matched_cps:
                    df_matched = pd.DataFrame(matched_cps)
                    st.dataframe(df_matched, use_container_width=True)

                    # 거래 제품 수정/삭제
                    with st.expander("🛠️ 선택 거래처 제품 수정/삭제"):
                        cp_names = [cp["prod_name"] for cp in matched_cps]
                        sel_cp_name = st.selectbox("수정/삭제할 제품 선택", cp_names)
                        target_cp = next(cp for cp in matched_cps if cp["prod_name"] == sel_cp_name)

                        edit_cp_price = st.number_input(
                            "공급가(엔, VAT별도) 수정",
                            min_value=0,
                            value=int(target_cp.get("supply_price", 0)),
                        )
                        edit_cp_jan_p = st.text_input("JAN(곽) 수정", value=target_cp.get("jan_pack", ""))

                        cpe1, cpe2 = st.columns(2)
                        if cpe1.button("제품 정보 수정 저장", disabled=is_visitor):
                            target_cp["supply_price"] = edit_cp_price
                            target_cp["jan_pack"] = edit_cp_jan_p
                            st.success("제품 정보가 수정되었습니다.")
                            st.rerun()
                        if cpe2.button("❌ 제품 삭제", disabled=not is_admin):
                            st.session_state.client_products.remove(target_cp)
                            st.success("제품이 삭제되었습니다.")
                            st.rerun()
                else:
                    st.info("이 거래처에 등록된 거래제품이 없습니다.")
            else:
                st.info("등록된 거래처가 없습니다.")

        # 2. 신규 거래처 등록
        with tab_c_reg:
            st.subheader("➕ 신규 거래처 등록")
            with st.form("new_client_form"):
                nc_name = st.text_input("거래처명 *")
                nc_zip = st.text_input("우편번호 (예: 100-0001)")
                nc_addr = st.text_input("주소 *")
                nc_phone = st.text_input("전화번호 *")

                nc_submit = st.form_submit_button("거래처 등록", disabled=is_visitor)

                if nc_submit:
                    if not nc_name or not nc_addr:
                        st.error("거래처명과 주소는 필수입니다.")
                    elif any(c["name"] == nc_name for c in st.session_state.clients):
                        st.error("이미 존재 거래처명입니다.")
                    else:
                        new_id = len(st.session_state.clients) + 1
                        st.session_state.clients.append({
                            "id": new_id,
                            "name": nc_name,
                            "zipcode": nc_zip,
                            "address": nc_addr,
                            "phone": nc_phone,
                        })
                        st.success(f"거래처 [{nc_name}] 등록 완료!")
                        st.rerun()

        # 3. 거래처 제품 등록
        with tab_cp_reg:
            st.subheader("📦 거래처 제품 등록")
            if not st.session_state.clients:
                st.warning("먼저 거래처를 등록해 주세요.")
            else:
                c_names = [c["name"] for c in st.session_state.clients]
                target_c_for_p = st.selectbox("대상 거래처 선택 *", c_names)

                with st.form("new_cp_form"):
                    ncp_name = st.text_input("상품명 *")
                    ncp_jan_p = st.text_input("JAN 코드 (곽)")
                    ncp_jan_s = st.text_input("JAN 코드 (낱장)")
                    ncp_price = st.number_input(
                        "공급가 (엔화 VAT 별도) *", min_value=0, step=100
                    )

                    ncp_submit = st.form_submit_button("거래제품 등록", disabled=is_visitor)

                    if ncp_submit:
                        if not ncp_name:
                            st.error("상품명은 필수입니다.")
                        else:
                            st.session_state.client_products.append({
                                "client_name": target_c_for_p,
                                "prod_name": ncp_name,
                                "jan_pack": ncp_jan_p,
                                "jan_single": ncp_jan_s,
                                "supply_price": ncp_price,
                            })
                            st.success(f"[{target_c_for_p}] 거래제품 [{ncp_name}] 등록 완료!")
                            st.rerun()

    # ------------------------------------------
    # 탭 5: 재고관리 (입고/출고)
    # ------------------------------------------
    elif menu == "재고관리 (입고/출고)":
        st.header("🔄 재고관리 (입고 및 출고 처리)")

        mode = st.radio("작업 선택", ["📥 입고 등록", "📤 출고 등록 (최대 30개 품목)"])

        if mode == "📥 입고 등록":
            st.subheader("📥 입고 등록 (창고별 재고 증가)")

            if not st.session_state.master_products:
                st.warning("먼저 마스터 상품을 등록해 주세요.")
            else:
                prod_map = {
                    f"[{p['code']}] {p['name']}": p
                    for p in st.session_state.master_products
                }
                sel_p_label = st.selectbox("입고할 마스터 상품 선택", list(prod_map.keys()))
                sel_p = prod_map[sel_p_label]

                with st.form("inbound_form"):
                    in_wh = st.selectbox("입고 창고 *", WAREHOUSES)
                    in_jan = st.text_input("JAN 코드", value=sel_p.get("jan_pack", ""))
                    in_price = st.number_input(
                        "매입단가(엔) *", min_value=0, value=int(sel_p["price"])
                    )
                    in_qty = st.number_input("입고 수량 *", min_value=1, value=10)

                    in_total = in_price * in_qty
                    st.write(f"**총 매입금액:** ¥ {in_total:,}")

                    in_submit = st.form_submit_button("입고 처리 완료", disabled=is_visitor)

                    if in_submit:
                        update_wh_stock(sel_p["code"], in_wh, in_qty)
                        st.session_state.stock_logs.append({
                            "date": tokyo_now.strftime("%Y-%m-%d %H:%M:%S"),
                            "type": "입고",
                            "wh": in_wh,
                            "client": "-",
                            "prod_name": sel_p["name"],
                            "jan": in_jan,
                            "qty": in_qty,
                            "unit_price": in_price,
                            "total_price": in_total,
                            "trade_type": "매입",
                            "manager": user["name"],
                        })
                        st.success(f"입고 완료! ({in_wh} 창고에 [{sel_p['name']}] {in_qty}개 추가됨)")
                        st.rerun()

        else:
            st.subheader("📤 출고 등록 (최대 30개 품목 묶음 등록)")

            if not st.session_state.clients:
                st.warning("먼저 거래처를 등록해 주세요.")
            else:
                client_names = [c["name"] for c in st.session_state.clients]
                sel_client_name = st.selectbox("1. 거래처 선택 *", client_names)

                selected_client_obj = next(
                    c for c in st.session_state.clients if c["name"] == sel_client_name
                )
                available_cps = [
                    cp
                    for cp in st.session_state.client_products
                    if cp["client_name"] == sel_client_name
                ]

                if not available_cps:
                    st.error("해당 거래처에 등록된 거래제품이 없습니다. 거래처 관리에서 제품을 먼저 등록하세요.")
                else:
                    st.markdown("---")
                    st.subheader("2. Delivery & Ship-to Information")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        out_wh = st.selectbox("출고 창고 선택 *", WAREHOUSES)
                        ship_to_name = st.text_input("납품처명 *", value=sel_client_name)
                    with col_b:
                        ship_to_addr = st.text_input(
                            "납품처 주소 *", value=selected_client_obj["address"]
                        )
                        ship_to_phone = st.text_input(
                            "납품처 전화번호 *", value=selected_client_obj["phone"]
                        )

                    st.markdown("---")
                    st.subheader("3. 출고 대상 제품 설정 (최대 30개)")

                    num_items = st.number_input(
                        "등록할 제품 종류 수", min_value=1, max_value=30, value=1
                    )

                    cp_labels = [f"{cp['prod_name']} (공급가: ¥{cp['supply_price']:,})" for cp in available_cps]

                    with st.form("outbound_multi_form"):
                        out_items_data = []

                        for i in range(int(num_items)):
                            st.write(f"**[제품 #{i+1}]**")
                            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

                            with c1:
                                sel_cp_idx = st.selectbox(
                                    f"제품 선택 #{i+1}",
                                    range(len(cp_labels)),
                                    format_func=lambda x: cp_labels[x],
                                    key=f"cp_sel_{i}",
                                )
                                cp_obj = available_cps[sel_cp_idx]
                            with c2:
                                trade_type = st.selectbox(
                                    f"거래방식 #{i+1}",
                                    ["납품", "FOC", "테스터"],
                                    key=f"trade_{i}",
                                )
                            with c3:
                                qty_val = st.number_input(
                                    f"수량 #{i+1}",
                                    min_value=1,
                                    value=1,
                                    key=f"qty_{i}",
                                )
                            with c4:
                                if trade_type in ["FOC", "테스터"]:
                                    final_unit_price = 0
                                    st.write("공급단가: **무료 (0엔)**")
                                else:
                                    final_unit_price = cp_obj["supply_price"]
                                    st.write(f"공급단가: **¥{final_unit_price:,}**")

                                calc_total = final_unit_price * qty_val
                                st.write(f"합계: **¥{calc_total:,}**")

                            out_items_data.append({
                                "cp_obj": cp_obj,
                                "trade_type": trade_type,
                                "qty": qty_val,
                                "unit_price": final_unit_price,
                                "total_price": calc_total,
                            })

                        out_submit = st.form_submit_button("일괄 출고 등록 완료", disabled=is_visitor)

                        if out_submit:
                            for item in out_items_data:
                                cp_o = item["cp_obj"]
                                matched_m = next(
                                    (
                                        m
                                        for m in st.session_state.master_products
                                        if m["name"] == cp_o["prod_name"]
                                    ),
                                    None,
                                )

                                if matched_m:
                                    update_wh_stock(matched_m["code"], out_wh, -item["qty"])

                                st.session_state.stock_logs.append({
                                    "date": tokyo_now.strftime("%Y-%m-%d %H:%M:%S"),
                                    "type": "출고",
                                    "wh": out_wh,
                                    "client": sel_client_name,
                                    "prod_name": cp_o["prod_name"],
                                    "jan": cp_o.get("jan_pack", ""),
                                    "qty": item["qty"],
                                    "unit_price": item["unit_price"],
                                    "total_price": item["total_price"],
                                    "trade_type": item["trade_type"],
                                    "manager": user["name"],
                                    "ship_to": f"{ship_to_name} / {ship_to_addr} / {ship_to_phone}",
                                })

                            st.success(
                                f"총 {len(out_items_data)}개 품목이 [{out_wh}] 창고에서 성공적으로 출고 처리되었습니다!"
                            )
                            st.rerun()

        st.markdown("---")
        st.subheader("📜 입출고 전체 이력")
        if st.session_state.stock_logs:
            df_logs = pd.DataFrame(st.session_state.stock_logs)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("입출고 이력이 존재하지 않습니다.")

    # ------------------------------------------
    # 탭 6: 타임카드 (휴가/월별 캘린더/휴무일 관리)
    # ------------------------------------------
    elif menu == "타임카드 (휴가/일정)":
        st.header("📆 타임카드 (휴가 신청 & 월별 캘린더)")

        rem_leave = user.get("annual_leave", 15.0)
        st.metric("나의 잔여 휴가(연차) 일수", f"{rem_leave:.1f} 일")

        st.markdown("---")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 휴가 / 일정 신청")
            with st.form("timecard_leave_form"):
                l_type = st.selectbox("신청 유형", ["연차", "반차", "병가", "경조사", "출장"])
                l_start = st.date_input("시작일")
                l_end = st.date_input("종료일")
                l_reason = st.text_area("사유")

                l_submit = st.form_submit_button("신청서 제출", disabled=is_visitor)

                if l_submit:
                    st.session_state.leave_records.append({
                        "applicant": user["name"],
                        "type": l_type,
                        "start_date": str(l_start),
                        "end_date": str(l_end),
                        "reason": l_reason,
                        "status": "승인 대기",
                    })
                    st.success("휴가 신청이 완료되었습니다.")
                    st.rerun()

            st.subheader("📋 휴가 결재 및 현황")
            if is_admin and st.session_state.leave_records:
                with st.expander("👑 [관리자 전용] 휴가 승인/반려"):
                    leave_idx = st.selectbox(
                        "결재할 휴가 항목 번호", range(len(st.session_state.leave_records))
                    )
                    b1, b2 = st.columns(2)
                    if b1.button("✅ 승인"):
                        target_l = st.session_state.leave_records[leave_idx]
                        target_l["status"] = "승인 완료"
                        # 승인 시 연차 차감
                        app_user = next(
                            (u for u in st.session_state.users if u["name"] == target_l["applicant"]),
                            None,
                        )
                        if app_user:
                            deduct = 0.5 if target_l["type"] == "반차" else 1.0
                            app_user["annual_leave"] = max(0.0, app_user.get("annual_leave", 15.0) - deduct)
                        st.success("승인 완료 및 잔여 연차가 차감되었습니다.")
                        st.rerun()
                    if b2.button("❌ 반려"):
                        st.session_state.leave_records[leave_idx]["status"] = "반려"
                        st.error("반려되었습니다.")
                        st.rerun()

            if st.session_state.leave_records:
                st.dataframe(pd.DataFrame(st.session_state.leave_records), use_container_width=True)

        with col2:
            st.subheader("🗓️ 월별 공유 캘린더 (휴무일 & 휴가)")

            # 관리자 전용 회사 휴무일/월차 등록
            if is_admin:
                with st.expander("👑 [관리자 전용] 회사 휴무일 / 공휴일 / 전체 월차 등록"):
                    with st.form("company_holiday_form"):
                        h_date = st.date_input("휴무일 날짜")
                        h_title = st.text_input("휴무명 (예: 창립기념일, 여름휴가)")
                        h_type = st.selectbox("구분", ["회사휴무", "공휴일", "전체월차"])
                        h_sub = st.form_submit_button("휴무일 등록")

                        if h_sub:
                            st.session_state.company_holidays.append({
                                "date": str(h_date),
                                "title": h_title,
                                "type": h_type,
                            })
                            st.success("휴무일이 등록되었습니다.")
                            st.rerun()

            # 연도 및 월 선택 (기본값: 현 시점)
            curr_y = tokyo_now.year
            curr_m = tokyo_now.month

            cy_col, cm_col = st.columns(2)
            sel_y = cy_col.number_input("연도 선택", min_value=2020, max_value=2030, value=curr_y)
            sel_m = cm_col.number_input("월 선택", min_value=1, max_value=12, value=curr_m)

            st.write(f"### 📅 {sel_y}년 {sel_m}월 캘린더")

            cal = calendar.monthcalendar(int(sel_y), int(sel_m))
            cal_df = pd.DataFrame(cal, columns=["월", "화", "수", "목", "금", "토", "일"])
            st.dataframe(cal_df, use_container_width=True)

            # 해당 월의 일정 및 휴가 목록 출력
            st.markdown("**📍 이번 달 주요 휴무 및 승인 휴가 목록:**")

            month_prefix = f"{sel_y}-{int(sel_m):02d}"

            # 회사 휴무일
            c_hols = [
                h
                for h in st.session_state.company_holidays
                if h["date"].startswith(month_prefix)
            ]
            for h in c_hols:
                st.write(f"🔴 **[회사휴무] {h['date']}:** {h['title']} ({h['type']})")

            # 직원 승인 휴가
            app_l = [
                l
                for l in st.session_state.leave_records
                if l["status"] == "승인 완료" and l["start_date"].startswith(month_prefix)
            ]
            for l in app_l:
                st.write(f"🔵 **[직원휴가] {l['applicant']}:** {l['type']} ({l['start_date']} ~ {l['end_date']})")

    # ------------------------------------------
    # 탭 7: 시스템 관리 (직원 관리 & 전체 계정 관리)
    # ------------------------------------------
    elif menu == "시스템 관리 (사용자/권한)":
        st.header("⚙️ 시스템 사용자 및 직원 전체 관리")

        tab_user_mgmt, tab_emp_mgmt = st.tabs(
            ["👥 전체 계정 수정/관리", "👔 직원 정보 관리 (입사일/연차)"]
        )

        # 1. 전체 계정 수정 및 관리
        with tab_user_mgmt:
            if is_admin:
                st.subheader("👑 승인 대기 계정")
                pending_users = [
                    u for u in st.session_state.users if u.get("status") == "승인 대기"
                ]
                if pending_users:
                    for pu in pending_users:
                        p1, p2, p3 = st.columns([2, 1, 1])
                        p1.write(
                            f"**ID:** {pu['id']} | **이름:** {pu['name']} ({pu['position']}) | **권한:** {pu['role']}"
                        )
                        if p2.button(f"승인 ({pu['id']})"):
                            pu["status"] = "승인 완료"
                            st.success(f"{pu['id']} 승인 완료")
                            st.rerun()
                        if p3.button(f"거절 ({pu['id']})"):
                            st.session_state.users.remove(pu)
                            st.rerun()
                else:
                    st.info("승인 대기 중인 계정이 없습니다.")

                st.markdown("---")
                st.subheader("🛠️ 계정 전체 정보 수정 (아이디/이름/직급/부서/권한)")

                user_ids = [u["id"] for u in st.session_state.users]
                sel_u_id = st.selectbox("수정할 계정 ID 선택", user_ids)
                target_u = next(u for u in st.session_state.users if u["id"] == sel_u_id)

                with st.form("edit_user_all_form"):
                    eu_name = st.text_input("이름", value=target_u["name"])
                    eu_pos = st.selectbox(
                        "직급",
                        POSITIONS,
                        index=POSITIONS.index(target_u.get("position", "사원"))
                        if target_u.get("position") in POSITIONS
                        else 0,
                    )
                    eu_dept = st.text_input("부서", value=target_u.get("dept", ""))
                    eu_role = st.selectbox(
                        "권한",
                        ROLES,
                        index=ROLES.index(target_u.get("role", "STAFF"))
                        if target_u.get("role") in ROLES
                        else 0,
                    )
                    eu_status = st.selectbox(
                        "승인 상태",
                        ["승인 완료", "승인 대기"],
                        index=0 if target_u.get("status") == "승인 완료" else 1,
                    )

                    eu_sub = st.form_submit_button("계정 정보 변경 저장")

                    if eu_sub:
                        target_u["name"] = eu_name
                        target_u["position"] = eu_pos
                        target_u["dept"] = eu_dept
                        target_u["role"] = eu_role
                        target_u["status"] = eu_status
                        st.success("계정 정보가 변경되었습니다.")
                        st.rerun()

            st.markdown("---")
            st.subheader("📋 전체 등록된 계정 현황")
            df_u = pd.DataFrame(st.session_state.users)[
                ["id", "name", "position", "dept", "role", "status", "hire_date", "annual_leave"]
            ]
            st.dataframe(df_u, use_container_width=True)

        # 2. 직원 관리 (입사일/잔여연차 수정)
        with tab_emp_mgmt:
            st.subheader("👔 직원 인사 정보 관리 (입사일 및 잔여 연차)")

            if not is_admin:
                st.warning("직원 정보 관리는 관리자 전용 기능입니다.")
            else:
                emp_ids = [u["id"] for u in st.session_state.users]
                sel_emp_id = st.selectbox("인사 정보를 관리할 직원 선택", emp_ids)
                target_emp = next(u for u in st.session_state.users if u["id"] == sel_emp_id)

                with st.form("emp_info_edit_form"):
                    st.write(f"**대상 직원:** {target_emp['name']} ({target_emp['id']})")
                    edit_hire_date = st.date_input(
                        "입사일 입력/수정",
                        value=datetime.datetime.strptime(
                            target_emp.get("hire_date", str(datetime.date.today())),
                            "%Y-%m-%d",
                        ).date(),
                    )
                    edit_leave_days = st.number_input(
                        "잔여 연차 일수 입력/수정",
                        min_value=0.0,
                        max_value=50.0,
                        value=float(target_emp.get("annual_leave", 15.0)),
                        step=0.5,
                    )

                    emp_save_sub = st.form_submit_button("인사 정보 저장")

                    if emp_save_sub:
                        target_emp["hire_date"] = str(edit_hire_date)
                        target_emp["annual_leave"] = edit_leave_days
                        st.success("직원의 입사일 및 잔여 연차가 성공적으로 저장되었습니다.")
                        st.rerun()

            st.markdown("---")
            st.subheader("📋 전체 직원 인사 정보 현황")
            df_emp = pd.DataFrame(st.session_state.users)[
                ["id", "name", "position", "dept", "hire_date", "annual_leave"]
            ]
            df_emp.columns = ["아이디", "이름", "직급", "부서", "입사일", "잔여연차(일)"]
            st.dataframe(df_emp, use_container_width=True)
