import datetime
import pandas as pd
import pytz
import streamlit as st

# ==========================================
# 0. Streamlit Metrics 에러 완전 무력화 패치
# ==========================================
try:
    import streamlit.runtime.metrics_util as _mu

    def _noop_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    _mu.gather_usage_stats = _noop_decorator
except Exception:
    pass

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="사내 통합 관리 시스템 (ERP)",
    page_layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 1. 세션 상태(데이터베이스 역할) 초기화
# ==========================================
if "users" not in st.session_state:
    st.session_state.users = [
        {
            "id": "admin",
            "pw": "admin123",
            "name": "관리자",
            "dept": "경영관리팀",
            "role": "시스템 관리자",
        }
    ]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "categories" not in st.session_state:
    st.session_state.categories = ["전자기기", "사무용품", "소모품", "가구/집기"]

if "master_products" not in st.session_state:
    st.session_state.master_products = []

if "purchase_orders" not in st.session_state:
    st.session_state.purchase_orders = []

if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = []

if "leave_records" not in st.session_state:
    st.session_state.leave_records = []


# --- 도쿄 기준 시간 계산 함수 ---
def get_tokyo_time():
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    return datetime.datetime.now(tokyo_tz)


# --- 근무시간 계산 함수 (09:00 시작 고정 / 12:00~13:00 점심 차감) ---
def calculate_work_hours(clock_in_str, clock_out_time):
    if not clock_out_time:
        return "근무 중"

    start_minutes = 9 * 60  # 09:00
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


# ==========================================
# 2. 로그인 화면
# ==========================================
if st.session_state.logged_in_user is None:
    st.title("🔒 사내 통합 관리 시스템 로그인")

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
                    st.session_state.logged_in_user = user
                    st.success(f"{user['name']}님 환영합니다!")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

# ==========================================
# 3. 메인 ERP 시스템 애플리케이션
# ==========================================
else:
    user = st.session_state.logged_in_user
    is_admin = user["role"] == "시스템 관리자" or user["id"] == "admin"

    # 사이드바 설정
    st.sidebar.title("🏢 WORK MANAGER")
    st.sidebar.write(f"**접속자:** {user['name']} ({user['id']})")
    st.sidebar.write(
        f"**권한:** {user['role']} {'👑 (관리자 권한)' if is_admin else ''}"
    )

    if st.sidebar.button("로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

    menu = st.sidebar.radio(
        "메뉴 이동",
        [
            "대시보드",
            "출퇴근 관리",
            "마스터 상품 등록/관리",
            "발주 등록/관리",
            "직원 계정 생성/관리",
            "휴가 및 스케줄 관리",
            "시스템 관리 (사용자 권한)",
        ],
    )

    tokyo_now = get_tokyo_time()
    st.info(
        f"🕒 **도쿄 기준 서버 시간 (Asia/Tokyo):** {tokyo_now.strftime('%Y-%m-%d %H:%M:%S')} JST"
    )

    # ------------------------------------------
    # 탭 1: 대시보드
    # ------------------------------------------
    if menu == "대시보드":
        st.header("📊 대시보드")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⏱️ 오늘 나의 출퇴근 현황")
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

            st.write(f"- **출근 기록 시각:** {clock_in_disp}")
            st.write(f"- **퇴근 기록 시각:** {clock_out_disp}")
            st.write(f"- **인정 실근무시간:** {work_hours_disp}")
            st.caption(
                "※ 근무시간 산정 기준: 출근 시각에 상관없이 09:00부터 계산되며, 12:00~13:00 점심시간 1시간이 자동 차감됩니다."
            )

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("☀️ 출근하기", use_container_width=True):
                    now_time_str = tokyo_now.strftime("%H:%M:%S")
                    if record and record["clockIn"]:
                        st.warning(
                            f"이미 오늘({record['clockIn']}) 출근 처리되었습니다."
                        )
                    else:
                        st.session_state.attendance_records.append({
                            "date": today_str,
                            "userId": user["id"],
                            "userName": user["name"],
                            "clockIn": now_time_str,
                            "clockOut": "--:--:--",
                            "calculatedHoursStr": "근무 중",
                        })
                        st.success(f"출근 완료! ({now_time_str})")
                        st.rerun()

            with btn_col2:
                if st.button("🌙 퇴근하기", use_container_width=True):
                    now_time = tokyo_now.time()
                    now_time_str = tokyo_now.strftime("%H:%M:%S")
                    if not record or not record["clockIn"]:
                        st.error("출근 기록이 존재하지 않습니다.")
                    else:
                        record["clockOut"] = now_time_str
                        record["calculatedHoursStr"] = calculate_work_hours(
                            record["clockIn"], now_time
                        )
                        st.success(f"퇴근 완료! ({now_time_str})")
                        st.rerun()

        with col2:
            st.subheader("📌 시스템 현황 요약")
            st.metric("등록된 마스터 상품 수", f"{len(st.session_state.master_products)} 개")
            st.metric("등록된 발주 건수", f"{len(st.session_state.purchase_orders)} 건")
            st.metric("전체 등록 직원 수", f"{len(st.session_state.users)} 명")

    # ------------------------------------------
    # 탭 2: 출퇴근 관리
    # ------------------------------------------
    elif menu == "출퇴근 관리":
        st.header("📅 출퇴근 이력 및 근무시간 조회")

        if is_admin and st.session_state.attendance_records:
            st.subheader("🛠️ 관리자 전용: 출퇴근 기록 삭제")
            del_idx = st.number_input(
                "삭제할 행 번호 (0부터 시작)",
                min_value=0,
                max_value=len(st.session_state.attendance_records) - 1,
                step=1,
            )
            if st.button("해당 출퇴근 기록 삭제"):
                del st.session_state.attendance_records[del_idx]
                st.success("기록이 삭제되었습니다.")
                st.rerun()

        if st.session_state.attendance_records:
            df_att = pd.DataFrame(st.session_state.attendance_records)
            df_att.columns = [
                "날짜",
                "사용자ID",
                "성명",
                "실제 출근시각",
                "퇴근시각",
                "인정 근무시간",
            ]
            st.dataframe(df_att, use_container_width=True)
        else:
            st.info("출퇴근 기록이 없습니다.")

    # ------------------------------------------
    # 탭 3: 마스터 상품 등록/관리
    # ------------------------------------------
    elif menu == "마스터 상품 등록/관리":
        st.header("📦 마스터 상품 등록 및 상세 관리")

        if is_admin:
            with st.expander("👑 [관리자 전용] 카테고리 신규 추가 / 삭제"):
                c_col1, c_col2 = st.columns([2, 1])
                with c_col1:
                    new_cat = st.text_input("새 카테고리명 입력")
                with c_col2:
                    st.write("")
                    st.write("")
                    if st.button("카테고리 추가"):
                        if (
                            new_cat
                            and new_cat not in st.session_state.categories
                        ):
                            st.session_state.categories.append(new_cat)
                            st.success(f"[{new_cat}] 카테고리가 추가되었습니다!")
                            st.rerun()
                        elif new_cat in st.session_state.categories:
                            st.warning("이미 존재하는 카테고리입니다.")

                st.write(
                    f"**현재 등록된 카테고리 목록:** {', '.join(st.session_state.categories)}"
                )

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("신규 마스터 상품 등록")
            with st.form("product_form"):
                p_code = st.text_input("상품 코드 * (예: PRD-1001)")
                p_name = st.text_input("상품명 * (예: 사무용 모니터 27인치)")
                p_category = st.selectbox(
                    "카테고리 선택 *", st.session_state.categories
                )
                p_unit = st.text_input("규격 / 단위 (예: EA, Box)")
                p_price = st.number_input(
                    "기본 단가(원) *", min_value=0, step=1000
                )
                p_stock = st.number_input("적정 재고량", min_value=0, step=1)
                p_vendor = st.text_input("제조사 / 공급업체")
                p_origin = st.text_input("원산지")
                p_barcode = st.text_input("바코드 / 식별번호")
                p_desc = st.text_area("상세 설명 및 특이사항")

                p_submit = st.form_submit_button("마스터 상품 등록")

                if p_submit:
                    if not p_code or not p_name:
                        st.error("상품 코드와 상품명은 필수 입력 항목입니다.")
                    elif any(
                        p["code"] == p_code
                        for p in st.session_state.master_products
                    ):
                        st.error("이미 존재하는 상품 코드입니다.")
                    else:
                        st.session_state.master_products.append({
                            "code": p_code,
                            "name": p_name,
                            "category": p_category,
                            "unit": p_unit,
                            "price": p_price,
                            "stock": p_stock,
                            "vendor": p_vendor,
                            "origin": p_origin,
                            "barcode": p_barcode,
                            "desc": p_desc,
                        })
                        st.success(f"마스터 상품 [{p_name}] 등록 완료!")
                        st.rerun()

        with col2:
            st.subheader("등록된 마스터 상품 목록")

            if is_admin and st.session_state.master_products:
                with st.expander("👑 [관리자 전용] 상품 삭제"):
                    prod_codes = [
                        p["code"] for p in st.session_state.master_products
                    ]
                    del_prod_code = st.selectbox(
                        "삭제할 상품 코드 선택", prod_codes
                    )
                    if st.button("선택 상품 삭제"):
                        st.session_state.master_products = [
                            p
                            for p in st.session_state.master_products
                            if p["code"] != del_prod_code
                        ]
                        st.success("상품이 삭제되었습니다.")
                        st.rerun()

            if st.session_state.master_products:
                df_prod = pd.DataFrame(st.session_state.master_products)
                df_prod.columns = [
                    "상품코드",
                    "상품명",
                    "카테고리",
                    "단위",
                    "기본단가",
                    "적정재고",
                    "공급업체",
                    "원산지",
                    "바코드",
                    "상세설명",
                ]
                st.dataframe(df_prod, use_container_width=True)
            else:
                st.info("등록된 마스터 상품이 없습니다.")

    # ------------------------------------------
    # 탭 4: 발주 등록/관리
    # ------------------------------------------
    elif menu == "발주 등록/관리":
        st.header("📝 발주 상세 정보 등록 및 관리")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("신규 발주 등록")
            if not st.session_state.master_products:
                st.warning("먼저 마스터 상품을 하나 이상 등록해주세요.")
            else:
                product_options = {
                    f"[{p['code']}] {p['name']} ({p['price']:,}원)": p
                    for p in st.session_state.master_products
                }
                selected_prod_label = st.selectbox(
                    "발주 대상 마스터 상품 선택 *",
                    list(product_options.keys()),
                )
                selected_prod = product_options[selected_prod_label]

                with st.form("po_form"):
                    po_vendor = st.text_input(
                        "발주처 / 공급업체 *", value=selected_prod["vendor"]
                    )
                    po_warehouse = st.selectbox(
                        "입고 예정 창고",
                        ["제1메인물류센터", "제2부자재창고", "본사 사무실"],
                    )
                    po_qty = st.number_input(
                        "발주 수량 *", min_value=1, value=10
                    )
                    po_unit_price = st.number_input(
                        "발주 단가(원) *",
                        min_value=0,
                        value=int(selected_prod["price"]),
                    )

                    po_total = po_qty * po_unit_price
                    st.write(f"**총 발주 금액:** {po_total:,} 원")

                    po_delivery = st.date_input("납기 요청일")
                    po_manager = st.text_input(
                        "발주 담당자", value=user["name"]
                    )
                    po_notes = st.text_area("상세 요청사항 및 비고")

                    po_submit = st.form_submit_button("발주 등록 완료")

                    if po_submit:
                        po_no = f"PO-{int(datetime.datetime.now().timestamp())}"
                        st.session_state.purchase_orders.append({
                            "orderNo": po_no,
                            "prodCode": selected_prod["code"],
                            "prodName": selected_prod["name"],
                            "vendor": po_vendor,
                            "warehouse": po_warehouse,
                            "qty": po_qty,
                            "unitPrice": po_unit_price,
                            "totalPrice": po_total,
                            "deliveryDate": str(po_delivery),
                            "manager": po_manager,
                            "notes": po_notes,
                            "status": "발주 요청 완료",
                        })
                        st.success(f"발주가 성공적으로 등록되었습니다! (발주번호: {po_no})")
                        st.rerun()

        with col2:
            st.subheader("발주 등록 내역 및 현황")

            if is_admin and st.session_state.purchase_orders:
                with st.expander("👑 [관리자 전용] 발주 상태 변경 및 삭제"):
                    po_nos = [
                        po["orderNo"]
                        for po in st.session_state.purchase_orders
                    ]
                    target_po_no = st.selectbox("관리할 발주번호 선택", po_nos)

                    target_po = next(
                        po
                        for po in st.session_state.purchase_orders
                        if po["orderNo"] == target_po_no
                    )

                    p_col1, p_col2 = st.columns(2)
                    with p_col1:
                        new_status = st.selectbox(
                            "발주 상태 변경",
                            ["발주 요청 완료", "승인 완료", "입고 완료", "발주 취소"],
                            index=0,
                        )
                        if st.button("상태 반영"):
                            target_po["status"] = new_status
                            st.success(f"상태가 [{new_status}](으)로 변경되었습니다.")
                            st.rerun()
                    with p_col2:
                        st.write("")
                        st.write("")
                        if st.button("해당 발주 삭제"):
                            st.session_state.purchase_orders = [
                                po
                                for po in st.session_state.purchase_orders
                                if po["orderNo"] != target_po_no
                            ]
                            st.success("발주 내역이 삭제되었습니다.")
                            st.rerun()

            if st.session_state.purchase_orders:
                df_po = pd.DataFrame(st.session_state.purchase_orders)
                df_po.columns = [
                    "발주번호",
                    "상품코드",
                    "상품명",
                    "공급업체",
                    "입고창고",
                    "수량",
                    "단가",
                    "총금액",
                    "납기요청일",
                    "담당자",
                    "비고/요청사항",
                    "진행상태",
                ]
                st.dataframe(df_po, use_container_width=True)
            else:
                st.info("등록된 발주 내역이 없습니다.")

    # ------------------------------------------
    # 탭 5: 직원 계정 생성/관리
    # ------------------------------------------
    elif menu == "직원 계정 생성/관리":
        st.header("👥 직원 계정 생성 및 관리")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("신규 직원 계정 생성")
            with st.form("emp_form"):
                e_id = st.text_input("아이디 *")
                e_pw = st.text_input("비밀번호 *", type="password")
                e_name = st.text_input("이름 *")
                e_dept = st.text_input("부서 *")
                e_role = st.selectbox("권한 역할", ["일반 직원", "시스템 관리자"])

                e_submit = st.form_submit_button("직원 계정 생성")

                if e_submit:
                    if not e_id or not e_pw or not e_name:
                        st.error("필수 항목을 모두 입력해주세요.")
                    elif any(u["id"] == e_id for u in st.session_state.users):
                        st.error("이미 존재하는 아이디입니다.")
                    else:
                        st.session_state.users.append({
                            "id": e_id,
                            "pw": e_pw,
                            "name": e_name,
                            "dept": e_dept,
                            "role": e_role,
                        })
                        st.success(f"신규 직원 [{e_name}] 계정 생성 완료!")
                        st.rerun()

        with col2:
            st.subheader("등록된 직원 목록")

            if is_admin and len(st.session_state.users) > 1:
                with st.expander("👑 [관리자 전용] 직원 계정 삭제"):
                    user_ids = [
                        u["id"]
                        for u in st.session_state.users
                        if u["id"] != "admin"
                    ]
                    if user_ids:
                        del_u_id = st.selectbox("삭제할 직원 ID", user_ids)
                        if st.button("해당 직원 계정 삭제"):
                            st.session_state.users = [
                                u
                                for u in st.session_state.users
                                if u["id"] != del_u_id
                            ]
                            st.success("계정이 삭제되었습니다.")
                            st.rerun()

            df_users = pd.DataFrame(st.session_state.users)[
                ["id", "name", "dept", "role"]
            ]
            df_users.columns = ["아이디", "이름", "부서", "권한 역할"]
            st.dataframe(df_users, use_container_width=True)

    # ------------------------------------------
    # 탭 6: 휴가 및 스케줄 관리
    # ------------------------------------------
    elif menu == "휴가 및 스케줄 관리":
        st.header("🌴 휴가 및 스케줄 관리")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("휴가 / 스케줄 신청")
            with st.form("leave_form"):
                l_type = st.selectbox("신청 유형", ["연차", "반차", "병가", "경조사"])
                l_start = st.date_input("시작일")
                l_end = st.date_input("종료일")
                l_reason = st.text_area("사유")

                l_submit = st.form_submit_button("신청서 제출")

                if l_submit:
                    st.session_state.leave_records.append({
                        "applicant": user["name"],
                        "type": l_type,
                        "period": f"{l_start} ~ {l_end}",
                        "reason": l_reason,
                        "status": "승인 대기",
                    })
                    st.success("휴가 신청이 완료되었습니다.")
                    st.rerun()

        with col2:
            st.subheader("휴가 신청 현황 및 결재")

            if is_admin and st.session_state.leave_records:
                with st.expander("👑 [관리자 전용] 휴가 결재 처리"):
                    leave_indices = list(
                        range(len(st.session_state.leave_records))
                    )
                    sel_leave_idx = st.selectbox(
                        "결재할 휴가 신청 번호 (행 순서)", leave_indices
                    )

                    l_col1, l_col2 = st.columns(2)
                    with l_col1:
                        if st.button("✅ 승인"):
                            st.session_state.leave_records[sel_leave_idx][
                                "status"
                            ] = "승인 완료"
                            st.success("휴가가 승인되었습니다.")
                            st.rerun()
                    with l_col2:
                        if st.button("❌ 반려"):
                            st.session_state.leave_records[sel_leave_idx][
                                "status"
                            ] = "반려"
                            st.error("휴가가 반려되었습니다.")
                            st.rerun()

            if st.session_state.leave_records:
                df_leave = pd.DataFrame(st.session_state.leave_records)
                df_leave.columns = ["신청자", "유형", "기간", "사유", "결재상태"]
                st.dataframe(df_leave, use_container_width=True)
            else:
                st.info("신청된 휴가 내역이 없습니다.")

    # ------------------------------------------
    # 탭 7: 시스템 관리 (사용자 권한)
    # ------------------------------------------
    elif menu == "시스템 관리 (사용자 권한)":
        st.header("⚙️ 시스템 사용자 권한 설정")
        st.write("각 역할 그룹별 메뉴 및 기능 권한 현황입니다.")

        perm_data = [
            {
                "역할 그룹": "시스템 관리자 (Administrator)",
                "접근 가능 메뉴": "전체 메뉴 (대시보드, 출퇴근, 마스터, 발주, 직원관리, 스케줄, 시스템관리)",
                "관리자 풀 권한": "카테고리 추가, 상품/발주/직원/출퇴근 삭제 및 휴가 결재 승인/반려 가능",
            },
            {
                "역할 그룹": "일반 직원 (User)",
                "접근 가능 메뉴": "대시보드, 출퇴근 관리, 마스터 상품 조회, 발주 등록, 휴가 신청",
                "관리자 풀 권한": "조회 및 본인 데이터 생성만 가능 (수정/삭제/결재 불가)",
            },
        ]
        st.table(pd.DataFrame(perm_data))
