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
# 1-1. 사용자 계정 (기본 admin)
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
        }
    ]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# 1-2. 기본 카테고리 및 창고 목록
if "categories" not in st.session_state:
    st.session_state.categories = ["전자기기", "사무용품", "소모품", "가구/집기", "화장품/뷰티"]

WAREHOUSES = ["SAGAWA", "L&K", "大吉商事"]
POSITIONS = ["사원", "주임", "대리", "과장", "차장", "부장", "팀장", "이사", "법인장"]
ROLES = ["관리자", "STAFF", "방문자"]

# 1-3. 마스터 상품 데이터
if "master_products" not in st.session_state:
    st.session_state.master_products = [
        {
            "code": "PRD-1001",
            "name": "샘플 스킨케어 세트",
            "category": "화장품/뷰티",
            "unit": "BOX",
            "price": 3000,
            "stock": 100,
            "vendor": "大吉商事",
            "origin": "한국",
            "barcode": "8801234567890",
            "desc": "기초 화장품 세트",
        }
    ]

# 1-4. 창고별 재고 데이터 (상품코드_창고명 : 수량)
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
            "name": "(주)도쿄유통",
            "zipcode": "100-0001",
            "address": "東京都千代田区1-1",
            "phone": "03-1234-5678",
        }
    ]

if "client_products" not in st.session_state:
    st.session_state.client_products = [
        {
            "client_name": "(주)도쿄유통",
            "prod_name": "샘플 스킨케어 세트",
            "jan": "4901234567890",
            "capacity": "500ml",
            "category": "화장품/뷰티",
            "supply_price": 4500,  # 엔화 VAT 별도
        }
    ]

# 1-6. 입출고 이력 데이터
if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = []

# 1-7. 근태 및 타임카드 데이터
if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = []

if "leave_records" not in st.session_state:
    st.session_state.leave_records = []


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


# 창고별 재고 수량 가져오기 함수
def get_wh_stock(prod_code, wh_name):
    key = f"{prod_code}_{wh_name}"
    return st.session_state.warehouse_stocks.get(key, 0)


# 창고별 재고 수량 변경 함수
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
                        })
                        st.success("계정 신청이 완료되었습니다! (관리자 승인 후 로그인 가능)")

# ==========================================
# 3. 메인 ERP 시스템 애플리케이션
# ==========================================
else:
    user = st.session_state.logged_in_user
    user_role = user.get("role", "방문자")
    is_admin = user_role == "관리자" or user["id"] == "admin"
    is_staff = user_role == "STAFF"
    is_visitor = user_role == "방문자"

    # 사이드바
    st.sidebar.title("🏢 WORK MANAGER")
    st.sidebar.write(f"**접속자:** {user['name']} ({user['position']})")
    st.sidebar.write(f"**권한:** {user_role} {'👑' if is_admin else ''}")

    if st.sidebar.button("로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

    menu = st.sidebar.radio(
        "메뉴 이동",
        [
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
    # 탭 1: 대시보드
    # ------------------------------------------
    if menu == "대시보드":
        st.header("📊 재고 및 보유 현황 대시보드")

        # 1. 전체 요약 지표
        total_items_type = len(st.session_state.master_products)

        # 총 재고 수량 및 총 재고 금액 계산
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

        # 2. 창고별 재고 현황
        st.subheader("🏢 창고별 재고 수량 현황")
        w_cols = st.columns(len(WAREHOUSES))
        for idx, wh in enumerate(WAREHOUSES):
            with w_cols[idx]:
                st.info(f"**{wh}**\n\n### {wh_summary[wh]:,} 개")

        st.markdown("---")

        # 3. 상품별 상세 보유 재고량 & 창고별 분배 현황
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
            st.caption("※ 근무시간 산정: 09:00 시작 기준, 12:00~13:00 점심시간 1시간 자동 차감")

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
    # 탭 3: 마스터 상품 등록/관리
    # ------------------------------------------
    elif menu == "마스터 상품 등록/관리":
        st.header("📦 마스터 상품 및 카테고리 관리")

        # 관리자 카테고리 수정/추가/삭제
        if is_admin:
            with st.expander("👑 [관리자 전용] 카테고리 전체 수정 및 추가/삭제"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    new_cat = st.text_input("신규 카테고리명 입력")
                    if st.button("카테고리 추가"):
                        if new_cat and new_cat not in st.session_state.categories:
                            st.session_state.categories.append(new_cat)
                            st.success(f"카테고리 [{new_cat}] 추가 완료!")
                            st.rerun()
                with c2:
                    del_cat = st.selectbox("삭제할 카테고리 선택", st.session_state.categories)
                    if st.button("선택 카테고리 삭제"):
                        st.session_state.categories.remove(del_cat)
                        st.success(f"카테고리 [{del_cat}] 삭제 완료!")
                        st.rerun()

        st.write(f"**현재 등록된 카테고리:** {', '.join(st.session_state.categories)}")
        st.markdown("---")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("신규 마스터 상품 등록")
            with st.form("product_form"):
                p_code = st.text_input("상품 코드 * (예: PRD-1002)")
                p_name = st.text_input("상품명 *")
                p_category = st.selectbox("카테고리 선택 *", st.session_state.categories)
                p_unit = st.text_input("규격 / 단위 (예: EA, Box)")
                p_price = st.number_input("기본 매입단가(엔) *", min_value=0, step=100)
                p_vendor = st.text_input("제조사 / 공급업체")
                p_origin = st.text_input("원산지")
                p_barcode = st.text_input("바코드 / 식별번호")
                p_desc = st.text_area("상세 설명")

                p_submit = st.form_submit_button("마스터 상품 등록", disabled=is_visitor)

                if p_submit:
                    if not p_code or not p_name:
                        st.error("상품 코드와 상품명은 필수 입력 항목입니다.")
                    elif any(p["code"] == p_code for p in st.session_state.master_products):
                        st.error("이미 존재하는 상품 코드입니다.")
                    else:
                        st.session_state.master_products.append({
                            "code": p_code,
                            "name": p_name,
                            "category": p_category,
                            "unit": p_unit,
                            "price": p_price,
                            "stock": 0,
                            "vendor": p_vendor,
                            "origin": p_origin,
                            "barcode": p_barcode,
                            "desc": p_desc,
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
                    edit_name = st.text_input("상품명 수정", value=target_prod["name"])
                    edit_cat = st.selectbox(
                        "카테고리 수정",
                        st.session_state.categories,
                        index=st.session_state.categories.index(target_prod["category"])
                        if target_prod["category"] in st.session_state.categories
                        else 0,
                    )
                    edit_price = st.number_input(
                        "매입단가(엔) 수정", min_value=0, value=int(target_prod["price"])
                    )
                    edit_vendor = st.text_input("공급업체 수정", value=target_prod["vendor"])
                    edit_barcode = st.text_input("바코드 수정", value=target_prod["barcode"])

                    btn_e1, btn_e2 = st.columns(2)
                    with btn_e1:
                        if st.button("수정사항 저장", disabled=is_visitor):
                            target_prod["name"] = edit_name
                            target_prod["category"] = edit_cat
                            target_prod["price"] = edit_price
                            target_prod["vendor"] = edit_vendor
                            target_prod["barcode"] = edit_barcode
                            st.success("상품 정보가 수정되었습니다.")
                            st.rerun()
                    with btn_e2:
                        if st.button("❌ 상품 삭제", disabled=not is_admin):
                            del st.session_state.master_products[sel_idx]
                            st.success("상품이 삭제되었습니다.")
                            st.rerun()

                st.markdown("---")
                df_prod = pd.DataFrame(st.session_state.master_products)
                df_prod.columns = [
                    "코드",
                    "상품명",
                    "카테고리",
                    "단위",
                    "매입단가(엔)",
                    "기본재고",
                    "공급업체",
                    "원산지",
                    "바코드",
                    "설명",
                ]
                st.dataframe(df_prod, use_container_width=True)
            else:
                st.info("등록된 상품이 없습니다.")

    # ------------------------------------------
    # 탭 4: 거래처 관리
    # ------------------------------------------
    elif menu == "거래처 관리":
        st.header("🤝 거래처 등록 및 거래처별 거래제품 관리")

        col1, col2 = st.columns([1, 1])

        # 1. 거래처 등록
        with col1:
            st.subheader("1. 신규 거래처 등록")
            with st.form("client_form"):
                c_name = st.text_input("거래처명 *")
                c_zip = st.text_input("우편번호 (예: 100-0001)")
                c_addr = st.text_input("주소 *")
                c_phone = st.text_input("전화번호 *")

                c_submit = st.form_submit_button("거래처 등록", disabled=is_visitor)

                if c_submit:
                    if not c_name or not c_addr:
                        st.error("거래처명과 주소는 필수입니다.")
                    else:
                        st.session_state.clients.append({
                            "name": c_name,
                            "zipcode": c_zip,
                            "address": c_addr,
                            "phone": c_phone,
                        })
                        st.success(f"거래처 [{c_name}] 등록 완료!")
                        st.rerun()

            st.subheader("등록된 거래처 목록")
            if st.session_state.clients:
                df_c = pd.DataFrame(st.session_state.clients)
                df_c.columns = ["거래처명", "우편번호", "주소", "전화번호"]
                st.dataframe(df_c, use_container_width=True)

        # 2. 거래처별 거래제품 등록
        with col2:
            st.subheader("2. 거래처별 거래제품 등록")
            if not st.session_state.clients:
                st.warning("먼저 거래처를 하나 이상 등록해주세요.")
            else:
                client_names = [c["name"] for c in st.session_state.clients]
                selected_client_name = st.selectbox("거래처 선택 *", client_names)

                with st.form("client_prod_form"):
                    cp_prod_name = st.text_input("제품명 *")
                    cp_jan = st.text_input("JAN 코드 (바코드)")
                    cp_capacity = st.text_input("용량 (예: 500ml, 100g)")
                    cp_cat = st.selectbox("제품 카테고리", st.session_state.categories)
                    cp_price = st.number_input(
                        "공급가(엔화, VAT별도) *", min_value=0, step=100
                    )

                    cp_submit = st.form_submit_button(
                        "거래제품 등록", disabled=is_visitor
                    )

                    if cp_submit:
                        if not cp_prod_name:
                            st.error("제품명은 필수 항목입니다.")
                        else:
                            st.session_state.client_products.append({
                                "client_name": selected_client_name,
                                "prod_name": cp_prod_name,
                                "jan": cp_jan,
                                "capacity": cp_capacity,
                                "category": cp_cat,
                                "supply_price": cp_price,
                            })
                            st.success(
                                f"[{selected_client_name}] 거래제품 [{cp_prod_name}] 등록 완료!"
                            )
                            st.rerun()

            st.subheader(
                f"[{selected_client_name if st.session_state.clients else ''}] 거래 제품 목록"
            )
            filtered_cp = [
                cp
                for cp in st.session_state.client_products
                if cp["client_name"] == selected_client_name
            ]
            if filtered_cp:
                df_cp = pd.DataFrame(filtered_cp)
                df_cp.columns = [
                    "거래처명",
                    "제품명",
                    "JAN",
                    "용량",
                    "카테고리",
                    "공급가(엔, VAT별도)",
                ]
                st.dataframe(df_cp, use_container_width=True)
            else:
                st.info("해당 거래처에 등록된 제품이 없습니다.")

    # ------------------------------------------
    # 탭 5: 재고관리 (입고/출고)
    # ------------------------------------------
    elif menu == "재고관리 (입고/출고)":
        st.header("🔄 재고관리 (입고 및 출고 처리)")

        mode = st.radio("작업 선택", ["📥 입고 등록", "📤 출고 등록 (최대 30개 품목)"])

        # ---------------- INBOUND ----------------
        if mode == "📥 입고 등록":
            st.subheader("📥 입고 등록 (창고별 재고 증가)")

            if not st.session_state.master_products:
                st.warning("먼저 마스터 상품을 등록해 주세요.")
            else:
                prod_map = {
                    f"[{p['code']}] {p['name']} (JAN: {p['barcode']})": p
                    for p in st.session_state.master_products
                }
                sel_p_label = st.selectbox("입고할 마스터 상품 선택", list(prod_map.keys()))
                sel_p = prod_map[sel_p_label]

                with st.form("inbound_form"):
                    in_wh = st.selectbox("입고 창고 *", WAREHOUSES)
                    in_jan = st.text_input("JAN 코드", value=sel_p["barcode"])
                    in_price = st.number_input(
                        "매입단가(엔) *", min_value=0, value=int(sel_p["price"])
                    )
                    in_qty = st.number_input("입고 수량 *", min_value=1, value=10)

                    in_total = in_price * in_qty
                    st.write(f"**총 매입금액:** ¥ {in_total:,}")

                    in_submit = st.form_submit_button("입고 처리 완료", disabled=is_visitor)

                    if in_submit:
                        # 재고 반영
                        update_wh_stock(sel_p["code"], in_wh, in_qty)
                        # 이력 저장
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
                        st.success(
                            f"입고 완료! ({in_wh} 창고에 [{sel_p['name']}] {in_qty}개 추가됨)"
                        )
                        st.rerun()

        # ---------------- OUTBOUND ----------------
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
                        ship_to_name = st.text_input(
                            "납품처명 (직접입력) *", value=sel_client_name
                        )
                    with col_b:
                        ship_to_addr = st.text_input(
                            "납품처 주소 (직접입력) *",
                            value=selected_client_obj["address"],
                        )
                        ship_to_phone = st.text_input(
                            "납품처 전화번호 (직접입력) *",
                            value=selected_client_obj["phone"],
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
                                # FOC / 테스터는 무료 처리
                                if trade_type in ["FOC", "테스터"]:
                                    final_unit_price = 0
                                    st.write("공급단가: **무료 (0엔)**")
                                else:
                                    final_unit_price = cp_obj["supply_price"]
                                    st.write(
                                        f"공급단가: **¥{final_unit_price:,}**"
                                    )

                                calc_total = final_unit_price * qty_val
                                st.write(f"합계: **¥{calc_total:,}**")

                            out_items_data.append({
                                "cp_obj": cp_obj,
                                "trade_type": trade_type,
                                "qty": qty_val,
                                "unit_price": final_unit_price,
                                "total_price": calc_total,
                            })

                        out_submit = st.form_submit_button(
                            "일괄 출고 등록 완료", disabled=is_visitor
                        )

                        if out_submit:
                            # 마스터 상품 매칭을 위한 검색
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

                                # 매칭되는 마스터 상품이 있다면 재고 차감
                                if matched_m:
                                    update_wh_stock(
                                        matched_m["code"], out_wh, -item["qty"]
                                    )

                                # 출고 이력 저장
                                st.session_state.stock_logs.append({
                                    "date": tokyo_now.strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "type": "출고",
                                    "wh": out_wh,
                                    "client": sel_client_name,
                                    "prod_name": cp_o["prod_name"],
                                    "jan": cp_o["jan"],
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
    # 탭 6: 타임카드 (휴가/일정 통합)
    # ------------------------------------------
    elif menu == "타임카드 (휴가/일정)":
        st.header("📆 타임카드 (근태/휴가 신청 & 월간 캘린더)")

        # 개인 잔여 휴가 계산 (기본 15일 부여 가정)
        used_leave_days = sum(
            1
            for l in st.session_state.leave_records
            if l["applicant"] == user["name"] and l["status"] == "승인 완료"
        )
        remaining_leave = 15 - used_leave_days

        c1, c2 = st.columns(2)
        c1.metric("나의 부여 휴가", "15 일")
        c2.metric("나의 잔여 휴가 일수", f"{remaining_leave} 일")

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

            st.subheader("📋 휴가 신청 내역 및 결재")
            if is_admin and st.session_state.leave_records:
                with st.expander("👑 [관리자 전용] 휴가 승인/반려"):
                    leave_idx = st.selectbox(
                        "결재할 휴가 항목 번호",
                        range(len(st.session_state.leave_records)),
                    )
                    b1, b2 = st.columns(2)
                    if b1.button("✅ 승인"):
                        st.session_state.leave_records[leave_idx]["status"] = (
                            "승인 완료"
                        )
                        st.success("승인되었습니다.")
                        st.rerun()
                    if b2.button("❌ 반려"):
                        st.session_state.leave_records[leave_idx]["status"] = "반려"
                        st.error("반려되었습니다.")
                        st.rerun()

            if st.session_state.leave_records:
                st.dataframe(
                    pd.DataFrame(st.session_state.leave_records),
                    use_container_width=True,
                )

        # 캘린더 보기
        with col2:
            st.subheader("🗓️ 이번 달 일정 및 휴가 캘린더")

            year = tokyo_now.year
            month = tokyo_now.month

            st.write(f"### 📅 {year}년 {month}월")

            cal = calendar.monthcalendar(year, month)
            cal_df = pd.DataFrame(
                cal,
                columns=["월", "화", "수", "목", "금", "토", "일"],
            )

            # 캘린더 형식 출력
            st.dataframe(
                cal_df.style.highlight_null(null_color="transparent"),
                use_container_width=True,
            )

            st.caption("📍 **이번 달 등록된 승인 휴가 목록:**")
            approved_leaves = [
                l
                for l in st.session_state.leave_records
                if l["status"] == "승인 완료"
            ]
            if approved_leaves:
                for al in approved_leaves:
                    st.write(
                        f"- **{al['applicant']}**: {al['type']} ({al['start_date']} ~ {al['end_date']})"
                    )
            else:
                st.write("승인된 휴가 일정이 없습니다.")

    # ------------------------------------------
    # 탭 7: 시스템 관리 (사용자/권한)
    # ------------------------------------------
    elif menu == "시스템 관리 (사용자/권한)":
        st.header("⚙️ 시스템 계정 승인 및 권한 관리")

        if is_admin:
            st.subheader("👑 [관리자 전용] 신규 계정 승인 및 권한 변경")

            pending_users = [
                u for u in st.session_state.users if u.get("status") == "승인 대기"
            ]

            if pending_users:
                st.warning(f"승인 대기 중인 계정이 {len(pending_users)}건 있습니다.")
                for pu in pending_users:
                    p_col1, p_col2, p_col3 = st.columns([2, 1, 1])
                    p_col1.write(
                        f"**ID:** {pu['id']} | **이름:** {pu['name']} ({pu['position']}) | **신청권한:** {pu['role']}"
                    )
                    if p_col2.button(f"승인 ({pu['id']})"):
                        pu["status"] = "승인 완료"
                        st.success(f"{pu['id']} 계정이 승인되었습니다.")
                        st.rerun()
                    if p_col3.button(f"거절 ({pu['id']})"):
                        st.session_state.users.remove(pu)
                        st.error(f"{pu['id']} 계정이 거절/삭제되었습니다.")
                        st.rerun()
            else:
                st.info("승인 대기 중인 신규 계정이 없습니다.")

            st.markdown("---")

        st.subheader("👥 전체 등록된 계정 현황")
        df_u = pd.DataFrame(st.session_state.users)[
            ["id", "name", "position", "dept", "role", "status"]
        ]
        df_u.columns = [
            "아이디",
            "이름",
            "직급",
            "부서",
            "권한",
            "승인상태",
        ]
        st.dataframe(df_u, use_container_width=True)

        st.markdown("---")
        st.subheader("🛡️ 권한별 기능 제한 안내")
        perm_info = [
            {
                "권한": "관리자 (Administrator)",
                "접근 및 기능 범위": "모든 항목 등록/수정/삭제 가능, 신규 회원 가입 승인, 카테고리 관리, 관리자 결재 권한",
            },
            {
                "권한": "STAFF",
                "접근 및 기능 범위": "출퇴근/휴가 신청, 마스터/거래처/입출고 등록 및 수정 가능 (삭제 및 관리자 전용 기능 제외)",
            },
            {
                "권한": "방문자 (Visitor)",
                "접근 및 기능 범위": "전체 ERP 시스템 **조회(Read-Only)**만 가능 (모든 등록/수정/삭제 버튼 비활성화)",
            },
        ]
        st.table(pd.DataFrame(perm_info))
