import datetime
import hashlib
import io
import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="기업 통합 ERP 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 1. Supabase 클라이언트 연결
# =========================================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("st.secrets 설정(SUPABASE_URL, SUPABASE_KEY)을 확인해주세요.")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# =========================================================
# 🔑 2. 로그인 화면
# =========================================================
if "user" not in st.session_state:
    st.title("🏢 기업 통합 ERP 시스템")
    
    with st.form("login_form"):
        username = st.text_input("아이디", value="admin")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인", use_container_width=True)
        
        if submitted:
            clean_username = username.strip()
            clean_password = password.strip()
            hashed_pw = hash_password(clean_password)
            
            try:
                res = supabase.table("user_profiles").select("*").eq("username", clean_username).execute()
                if res.data:
                    user = res.data[0]
                    if user.get("password_hash") == hashed_pw:
                        st.session_state["user"] = user
                        st.success(f"{user['full_name']}님 환영합니다!")
                        st.rerun()
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.error("존재하지 않는 아이디입니다.")
            except Exception as e:
                st.error(f"로그인 오류: {e}")

# =========================================================
# 📊 3. 메인 시스템 화면
# =========================================================
else:
    user = st.session_state["user"]
    
    # 사이드바 사용자 정보 & 로그아웃
    st.sidebar.title("🏢 ERP 시스템")
    st.sidebar.subheader(f"👤 {user['full_name']} ({user['username']})")
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        del st.session_state["user"]
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # 메뉴 구성
    menu_options = [
        "📊 대시보드",
        "🏷️ 상품 마스터 관리",
        "🤝 거래처 관리",
        "📦 입출고 관리 & 엑셀등록",
        "⏰ 출퇴근 조회 및 기록",
        "📅 직원 캘린더"
    ]
    selected_menu = st.sidebar.radio("📌 메뉴 선택", menu_options)
    st.sidebar.markdown("---")

    # ---------------------------------------------------------
    # 📊 1. 대시보드 (엔화 기준, 출고건 매출 집계)
    # ---------------------------------------------------------
    if selected_menu == "📊 대시보드":
        st.title("📊 경영 요약 대시보드")
        
        # 이번 달 데이터 집계
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1).strftime("%Y-%m-%d")
        
        try:
            # 입고/출고 내역 가져오기
            tx_res = supabase.table("inventory_transactions") \
                .select("*") \
                .gte("transaction_date", first_day_of_month) \
                .execute()
            
            df_tx = pd.DataFrame(tx_res.data) if tx_res.data else pd.DataFrame()
            
            in_count = 0
            out_count = 0
            total_sales_jpy = 0
            
            if not df_tx.empty:
                in_count = df_tx[df_tx["transaction_type"] == "IN"]["qty"].sum()
                out_df = df_tx[(df_tx["transaction_type"] == "OUT") & (df_tx["status"] == "COMPLETED")]
                out_count = out_df["qty"].sum()
                total_sales_jpy = out_df["total_price_jpy"].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📦 이번 달 입고 수량", f"{in_count:,} 개")
            col2.metric("🚚 이번 달 출고 수량", f"{out_count:,} 개")
            col3.metric("💴 이번 달 출고 매출액", f"¥ {total_sales_jpy:,.0f}")
            
            st.markdown("---")
            st.subheader("📋 최근 출고 완료 건 (매출 반영 내역)")
            if not df_tx.empty and not out_df.empty:
                st.dataframe(out_df[["transaction_date", "product_code", "client_name", "qty", "unit_price_jpy", "total_price_jpy"]], use_container_width=True)
            else:
                st.info("이번 달 완료된 출고(매출) 내역이 없습니다.")
                
        except Exception as e:
            st.error(f"대시보드 데이터를 불러오는 중 오류 발생: {e}")

    # ---------------------------------------------------------
    # 🏷️ 2. 상품 마스터 관리
    # ---------------------------------------------------------
    elif selected_menu == "🏷️ 상품 마스터 관리":
        st.title("🏷️ 취급 상품 마스터 관리")
        
        with st.expander("➕ 신규 상품 등록", expanded=False):
            with st.form("add_product_form"):
                p_code = st.text_input("상품 코드 (예: PROD-001)")
                p_name = st.text_input("상품명")
                p_cat = st.selectbox("카테고리", ["전자기기", "사무용품", "식품", "의류", "기타"])
                p_price = st.number_input("기준 단가 (엔화 ¥)", min_value=0, value=1000)
                
                if st.form_submit_button("상품 등록"):
                    if p_code and p_name:
                        supabase.table("products").insert({
                            "product_code": p_code.strip(),
                            "product_name": p_name.strip(),
                            "category": p_cat,
                            "standard_price_jpy": p_price
                        }).execute()
                        st.success("상품이 성공적으로 등록되었습니다!")
                        st.rerun()

        st.subheader("📦 등록된 상품 목록")
        prod_res = supabase.table("products").select("*").execute()
        if prod_res.data:
            st.dataframe(pd.DataFrame(prod_res.data), use_container_width=True)
        else:
            st.info("등록된 상품이 없습니다.")

    # ---------------------------------------------------------
    # 🤝 3. 거래처 관리 (공급가율 설정)
    # ---------------------------------------------------------
    elif selected_menu == "🤝 거래처 관리 및 공급가 설정":
        st.title("🤝 거래처 관리")
        
        with st.expander("➕ 신규 거래처 등록", expanded=False):
            with st.form("add_client_form"):
                c_name = st.text_input("거래처명")
                c_type = st.selectbox("거래처 구분", ["BUYER (매출처/고객)", "VENDOR (매입처/공급사)"])
                c_rate = st.number_input("적용 공급가율 (%) - 예: 90이면 기준가의 90%로 자동계산", min_value=1.0, max_value=200.0, value=100.0)
                
                if st.form_submit_button("거래처 등록"):
                    if c_name:
                        type_code = "BUYER" if "BUYER" in c_type else "VENDOR"
                        supabase.table("clients").insert({
                            "client_name": c_name.strip(),
                            "client_type": type_code,
                            "discount_rate": c_rate
                        }).execute()
                        st.success("거래처가 등록되었습니다.")
                        st.rerun()

        st.subheader("📋 등록된 거래처 목록")
        client_res = supabase.table("clients").select("*").execute()
        if client_res.data:
            st.dataframe(pd.DataFrame(client_res.data), use_container_width=True)

    # ---------------------------------------------------------
    # 📦 4. 입출고 관리 & 엑셀 등록 (거래처별 공급가 자동 적용)
    # ---------------------------------------------------------
    elif selected_menu == "📦 입출고 관리 & 엑셀등록":
        st.title("📦 입출고 관리 & 거래처별 공급가 자동 계산")
        
        tab1, tab2 = st.tabs(["📝 건별 등록", "📂 엑셀 일괄 등록"])
        
        # 거래처 및 상품 데이터 사전 조회
        clients_data = supabase.table("clients").select("*").execute().data or []
        products_data = supabase.table("products").select("*").execute().data or []
        
        client_dict = {c["client_name"]: c["discount_rate"] for c in clients_data}
        product_dict = {p["product_code"]: p["standard_price_jpy"] for p in products_data}
        
        with tab1:
            with st.form("single_tx_form"):
                tx_type = st.radio("구분", ["IN (입고)", "OUT (출고)"], horizontal=True)
                sel_product = st.selectbox("상품 선택 (코드)", list(product_dict.keys()) if product_dict else ["등록된 상품 없음"])
                sel_client = st.selectbox("거래처 선택", list(client_dict.keys()) if client_dict else ["등록된 거래처 없음"])
                qty = st.number_input("수량", min_value=1, value=10)
                
                # 공급가 자동 계산
                std_price = product_dict.get(sel_product, 0)
                rate = client_dict.get(sel_client, 100.0)
                calc_unit_price = (std_price * rate) / 100.0
                calc_total = calc_unit_price * qty
                
                st.info(f"💡 기준단가: ¥{std_price:,.0f} | 거래처 공급가율: {rate}% -> **적용 단가: ¥{calc_unit_price:,.0f}** | **총액: ¥{calc_total:,.0f}**")
                
                if st.form_submit_button("입출고 내역 저장"):
                    t_code = "IN" if "IN" in tx_type else "OUT"
                    supabase.table("inventory_transactions").insert({
                        "transaction_type": t_code,
                        "product_code": sel_product,
                        "client_name": sel_client,
                        "qty": qty,
                        "unit_price_jpy": calc_unit_price,
                        "total_price_jpy": calc_total,
                        "status": "COMPLETED"
                    }).execute()
                    
                    # 수량 업데이트
                    stock_change = qty if t_code == "IN" else -qty
                    curr_stock = next((p["current_stock"] for p in products_data if p["product_code"] == sel_product), 0)
                    supabase.table("products").update({"current_stock": curr_stock + stock_change}).eq("product_code", sel_product).execute()
                    
                    st.success("입출고 처리가 완료되었습니다.")
                    st.rerun()
                    
        with tab2:
            st.subheader("📂 엑셀 파일로 일괄 등록")
            st.caption("엑셀 컬럼 양식: `구분(IN/OUT)`, `상품코드`, `거래처명`, `수량`")
            uploaded_file = st.file_uploader("엑셀 파일(.xlsx, .csv) 업로드", type=["xlsx", "csv"])
            
            if uploaded_file:
                try:
                    df_upload = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
                    st.write("📌 업로드 데이터 미리보기:", df_upload.head())
                    
                    if st.button("🚀 DB에 일괄 등록하기"):
                        for _, row in df_upload.iterrows():
                            t_type = str(row["구분"]).upper().strip()
                            p_code = str(row["상품코드"]).strip()
                            c_name = str(row["거래처명"]).strip()
                            t_qty = int(row["수량"])
                            
                            std_p = product_dict.get(p_code, 0)
                            disc_r = client_dict.get(c_name, 100.0)
                            u_price = (std_p * disc_r) / 100.0
                            tot_price = u_price * t_qty
                            
                            supabase.table("inventory_transactions").insert({
                                "transaction_type": t_type,
                                "product_code": p_code,
                                "client_name": c_name,
                                "qty": t_qty,
                                "unit_price_jpy": u_price,
                                "total_price_jpy": tot_price,
                                "status": "COMPLETED"
                            }).execute()
                        st.success("엑셀 일괄 등록이 성공적으로 완료되었습니다!")
                        st.rerun()
                except Exception as e:
                    st.error(f"엑셀 처리 오류: {e}")

    # ---------------------------------------------------------
    # ⏰ 5. 출퇴근 조회 및 기록
    # ---------------------------------------------------------
    elif selected_menu == "⏰ 출퇴근 조회 및 기록":
        st.title("⏰ 직원 출퇴근 관리")
        
        col1, col2 = st.columns(2)
        now_time = datetime.datetime.now()
        
        with col1:
            st.subheader(f"현 시각: {now_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if st.button("🟢 출근 등록", use_container_width=True):
                supabase.table("attendance").insert({
                    "username": user["username"],
                    "full_name": user["full_name"],
                    "work_date": datetime.date.today().strftime("%Y-%m-%d"),
                    "clock_in": now_time.strftime("%H:%M:%S"),
                    "status": "근무중"
                }).execute()
                st.success("출근이 기록되었습니다.")
                st.rerun()
                
        with col2:
            st.write("")
            st.write("")
            if st.button("🔴 퇴근 등록", use_container_width=True):
                # 오늘 출근 기록 찾아서 퇴근시간 업데이트
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                att_res = supabase.table("attendance").select("*").eq("username", user["username"]).eq("work_date", today_str).execute()
                if att_res.data:
                    record_id = att_res.data[-1]["id"]
                    supabase.table("attendance").update({
                        "clock_out": now_time.strftime("%H:%M:%S"),
                        "status": "퇴근완료"
                    }).eq("id", record_id).execute()
                    st.success("퇴근이 기록되었습니다.")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 전체 직원 출퇴근 현황")
        att_all = supabase.table("attendance").select("*").order("created_at", desc=True).execute()
        if att_all.data:
            st.dataframe(pd.DataFrame(att_all.data)[["work_date", "full_name", "clock_in", "clock_out", "status"]], use_container_width=True)

    # ---------------------------------------------------------
    # 📅 6. 직원 캘린더
    # ---------------------------------------------------------
    elif selected_menu == "📅 직원 캘린더":
        st.title("📅 사내 일정 및 직원 캘린더")
        
        with st.form("add_event_form"):
            e_title = st.text_input("일정 제목")
            e_date = st.date_input("날짜", datetime.date.today())
            e_desc = st.text_area("일정 상세 설명")
            
            if st.form_submit_button("일정 추가"):
                if e_title:
                    supabase.table("calendar_events").insert({
                        "title": e_title,
                        "event_date": e_date.strftime("%Y-%m-%d"),
                        "created_by": user["full_name"],
                        "description": e_desc
                    }).execute()
                    st.success("일정이 추가되었습니다.")
                    st.rerun()

        st.subheader("📌 등록된 사내 일정 목록")
        events_res = supabase.table("calendar_events").select("*").order("event_date", desc=False).execute()
        if events_res.data:
            for ev in events_res.data:
                st.write(f"📅 **[{ev['event_date']}]** {ev['title']} *(작성자: {ev['created_by']})*")
                if ev.get("description"):
                    st.caption(f"↳ {ev['description']}")
                st.markdown("---")
