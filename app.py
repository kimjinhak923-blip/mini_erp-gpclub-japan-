import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo  # pytz 대신 zoneinfo 사용
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# 한국/일본 표준시 설정
JST = ZoneInfo("Asia/Tokyo")  # Asia_Tokyo 대신 Asia/Tokyo 표준 이름 사용


# --- 2. Supabase 클라이언트 연결 ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Supabase 연결 실패: {e}")
    st.stop()


# --- 3. 비밀번호 해싱 함수 ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# --- 4. 세션 상태 초기화 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None


# --- 5. 로그인 화면 ---
def login_page():
    st.title("🏢 GPClub Japan Mini ERP")
    st.subheader("로그인")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("아이디").strip()
        password = st.text_input("비밀번호", type="password")
        submit = st.form_submit_button("로그인")

        if submit:
            if not username or not password:
                st.warning("아이디와 비밀번호를 모두 입력해 주세요.")
                return

            try:
                # user_profiles 테이블에서 아이디 조회
                response = (
                    supabase.table("user_profiles")
                    .select("*")
                    .eq("username", username)
                    .execute()
                )

                if not response.data or len(response.data) == 0:
                    st.error("존재하지 않는 아이디입니다.")
                    return

                user = response.data[0]
                hashed_input = hash_password(password)

                # 비밀번호 검증 (해시값 비교 또는 평문 비교 하이브리드)
                if (
                    user.get("password_hash") == hashed_input
                    or user.get("password_hash") == password
                ):
                    st.session_state.logged_in = True
                    st.session_state.user_info = user
                    st.success(f"{user['full_name']}님, 환영합니다!")
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")

            except Exception as e:
                st.error(f"로그인 처리 중 오류 발생: {e}")


# --- 6. 메인 ERP 화면 ---
def main_page():
    user = st.session_state.user_info

    # 사이드바 (사용자 정보 & 로그아웃)
    with st.sidebar:
        st.write(f"👤 **{user['full_name']}** ({user['role']})")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
        st.divider()

    # 메인 탭 구성
    tabs = st.tabs(
        [
            "⏰ 출퇴근 관리",
            "📦 상품 마스터",
            "🤝 거래처 관리",
            "📊 입출고/매출 관리",
            "📅 일정 캘린더",
        ]
    )

    # --------------------------------------------------
    # TAB 1: 출퇴근 관리
    # --------------------------------------------------
    with tabs[0]:
        st.header("⏰ 출퇴근 기록")
        col1, col2 = st.columns(2)
        now_jst = datetime.now(JST)
        today_date = now_jst.strftime("%Y-%m-%d")
        now_time = now_jst.strftime("%H:%M:%S")

        with col1:
            if st.button("🔴 출근하기", use_container_width=True):
                try:
                    supabase.table("attendance").insert(
                        {
                            "username": user["username"],
                            "full_name": user["full_name"],
                            "work_date": today_date,
                            "clock_in": now_time,
                            "status": "근무중",
                        }
                    ).execute()
                    st.success(f"{now_time} 출근 등록 완료!")
                    st.rerun()
                except Exception as e:
                    st.error(f"출근 처리 오류: {e}")

        with col2:
            if st.button("🔵 퇴근하기", use_container_width=True):
                try:
                    supabase.table("attendance").update(
                        {"clock_out": now_time, "status": "퇴근"}
                    ).eq("username", user["username"]).eq(
                        "work_date", today_date
                    ).execute()
                    st.success(f"{now_time} 퇴근 등록 완료!")
                    st.rerun()
                except Exception as e:
                    st.error(f"퇴근 처리 오류: {e}")

        st.subheader("오늘의 출퇴근 현황")
        att_res = (
            supabase.table("attendance")
            .select("*")
            .eq("work_date", today_date)
            .execute()
        )
        if att_res.data:
            st.dataframe(pd.DataFrame(att_res.data), use_container_width=True)
        else:
            st.info("오늘 등록된 출퇴근 내역이 없습니다.")

    # --------------------------------------------------
    # TAB 2: 상품 마스터
    # --------------------------------------------------
    with tabs[1]:
        st.header("📦 상품 마스터 관리")

        with st.expander("➕ 신규 상품 등록"):
            with st.form("new_product_form"):
                p_code = st.text_input("상품 코드 (필수)")
                p_name = st.text_input("상품명 (필수)")
                p_cat = st.text_input("카테고리")
                p_price = st.number_input(
                    "기준가 (엔화 JPY)", min_value=0.0, step=10.0
                )
                p_stock = st.number_input("초기 재고량", min_value=0, step=1)
                p_submit = st.form_submit_button("상품 저장")

                if p_submit and p_code and p_name:
                    try:
                        supabase.table("products").insert(
                            {
                                "product_code": p_code,
                                "product_name": p_name,
                                "category": p_cat,
                                "standard_price_jpy": p_price,
                                "current_stock": p_stock,
                            }
                        ).execute()
                        st.success("상품이 성공적으로 등록되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"상품 등록 오류: {e}")

        prod_res = (
            supabase.table("products")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        if prod_res.data:
            st.dataframe(pd.DataFrame(prod_res.data), use_container_width=True)

    # --------------------------------------------------
    # TAB 3: 거래처 관리
    # --------------------------------------------------
    with tabs[2]:
        st.header("🤝 거래처 및 공급가율 관리")

        with st.expander("➕ 신규 거래처 등록"):
            with st.form("new_client_form"):
                c_name = st.text_input("거래처명 (필수)")
                c_type = st.selectbox(
                    "구분", ["BUYER", "VENDOR"], format_func=lambda x: "매출처(BUYER)" if x == "BUYER" else "매입처(VENDOR)"
                )
                c_rate = st.number_input(
                    "기본 공급가율 (%)", min_value=0.0, max_value=200.0, value=100.0
                )
                c_submit = st.form_submit_button("거래처 저장")

                if c_submit and c_name:
                    try:
                        supabase.table("clients").insert(
                            {
                                "client_name": c_name,
                                "client_type": c_type,
                                "discount_rate": c_rate,
                            }
                        ).execute()
                        st.success("거래처가 등록되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"거래처 등록 오류: {e}")

        client_res = (
            supabase.table("clients")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        if client_res.data:
            st.dataframe(pd.DataFrame(client_res.data), use_container_width=True)

    # --------------------------------------------------
    # TAB 4: 입출고/매출 관리
    # --------------------------------------------------
    with tabs[3]:
        st.header("📊 입출고 및 매출 등록")

        products_list = (
            supabase.table("products").select("product_code, product_name").execute().data
            or []
        )
        clients_list = (
            supabase.table("clients").select("client_name").execute().data or []
        )

        with st.form("inventory_form"):
            t_type = st.radio("거래 유형", ["IN", "OUT"], format_func=lambda x: "입고 (IN)" if x == "IN" else "출고 (OUT)")
            p_select = st.selectbox(
                "상품 선택",
                options=[p["product_code"] for p in products_list],
                format_func=lambda x: next(
                    (f"{p['product_name']} ({p['product_code']})" for p in products_list if p["product_code"] == x), x
                ) if products_list else "등록된 상품 없음",
            )
            c_select = st.selectbox(
                "거래처 선택",
                options=[c["client_name"] for c in clients_list] if clients_list else ["기타"],
            )
            qty = st.number_input("수량", min_value=1, value=1)
            unit_price = st.number_input("적용 단가 (엔화 JPY)", min_value=0.0, value=0.0)
            t_submit = st.form_submit_button("거래 내역 저장")

            if t_submit and p_select:
                try:
                    total_price = qty * unit_price
                    supabase.table("inventory_transactions").insert(
                        {
                            "transaction_type": t_type,
                            "product_code": p_select,
                            "client_name": c_select,
                            "qty": qty,
                            "unit_price_jpy": unit_price,
                            "total_price_jpy": total_price,
                            "status": "COMPLETED",
                        }
                    ).execute()

                    # 재고 수량 업데이트
                    prod_data = (
                        supabase.table("products")
                        .select("current_stock")
                        .eq("product_code", p_select)
                        .execute()
                        .data
                    )
                    if prod_data:
                        curr_stock = prod_data[0]["current_stock"] or 0
                        new_stock = curr_stock + qty if t_type == "IN" else curr_stock - qty
                        supabase.table("products").update(
                            {"current_stock": new_stock}
                        ).eq("product_code", p_select).execute()

                    st.success("입출고 거래 등록 및 재고 업데이트가 완료되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"거래 등록 오류: {e}")

        st.subheader("최근 거래 내역")
        tx_res = (
            supabase.table("inventory_transactions")
            .select("*")
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        if tx_res.data:
            st.dataframe(pd.DataFrame(tx_res.data), use_container_width=True)

    # --------------------------------------------------
    # TAB 5: 일정 캘린더
    # --------------------------------------------------
    with tabs[4]:
        st.header("📅 직원 일정 캘린더")

        with st.expander("➕ 일정 추가"):
            with st.form("calendar_form"):
                e_title = st.text_input("일정 제목 (필수)")
                e_date = st.date_input("날짜")
                e_desc = st.text_area("상세 내용")
                e_submit = st.form_submit_button("일정 저장")

                if e_submit and e_title:
                    try:
                        supabase.table("calendar_events").insert(
                            {
                                "title": e_title,
                                "event_date": str(e_date),
                                "created_by": user["full_name"],
                                "description": e_desc,
                            }
                        ).execute()
                        st.success("일정이 추가되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"일정 추가 오류: {e}")

        events_res = (
            supabase.table("calendar_events")
            .select("*")
            .order("event_date", desc=False)
            .execute()
        )
        if events_res.data:
            st.dataframe(pd.DataFrame(events_res.data), use_container_width=True)


# --- 7. 앱 실행 진입점 ---
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_page()
