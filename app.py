import datetime
import hashlib
import pytz
import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="차세대 기업 통합 ERP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 도쿄 타임존 (JST)
TOKYO_TZ = pytz.timezone('Asia/Tokyo')

def get_tokyo_now():
    return datetime.datetime.now(TOKYO_TZ)

# 1. Supabase Client
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("st.secrets에 SUPABASE_URL 및 SUPABASE_KEY 설정이 필요합니다.")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ---------------------------------------------------------
# 🔑 로그인 및 회원가입
# ---------------------------------------------------------
if "user" not in st.session_state:
    st.title("🏢 차세대 기업 통합 ERP 시스템")
    
    tab1, tab2 = st.tabs(["🔑 로그인", "📝 회원가입 신청"])
    
    with tab1:
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
                        if user.get("password_hash") != hashed_pw:
                            st.error("❌ 비밀번호가 올바르지 않습니다.")
                        elif user.get("status") == "PENDING":
                            st.warning("⏳ 관리자의 가입 승인 대기 중인 계정입니다.")
                        elif user.get("status") == "REJECTED":
                            st.error("❌ 가입 신청이 거절된 계정입니다.")
                        elif not user.get("is_active", True):
                            st.error("❌ 비활성화된 계정입니다.")
                        else:
                            st.session_state["user"] = user
                            st.success(f"🎉 {user['full_name']}님 환영합니다!")
                            st.rerun()
                    else:
                        st.error("❌ 존재하지 않는 아이디입니다.")
                except Exception as e:
                    st.error(f"로그인 처리 중 오류 발생: {e}")

    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("신청 아이디")
            new_password = st.text_input("신청 비밀번호", type="password")
            full_name = st.text_input("이름")
            
            role_display = st.selectbox("희망 권한", ["일반 사원", "관리자"])
            role_code = "ADMIN" if role_display == "관리자" else "STAFF"
            
            signup_submitted = st.form_submit_button("가입 신청 제출", use_container_width=True)
            
            if signup_submitted and new_username and new_password and full_name:
                try:
                    supabase.table("user_profiles").insert({
                        "username": new_username.strip(),
                        "password_hash": hash_password(new_password.strip()),
                        "full_name": full_name.strip(),
                        "role": role_code,
                        "status": "PENDING",
                        "is_active": True
                    }).execute()
                    st.success("✅ 가입 신청이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.")
                except Exception as e:
                    st.error(f"가입 신청 실패 (아이디 중복 확인 필요): {e}")

# ---------------------------------------------------------
# 📊 로그인 후 메인 화면
# ---------------------------------------------------------
else:
    user = st.session_state["user"]
    tokyo_now = get_tokyo_now()
    
    # 상단 헤더: 실시간 도쿄 시각 & 빠른 출퇴근 버튼
    st.markdown(f"### 📍 **현재 시각 (도쿄 JST):** `{tokyo_now.strftime('%Y-%m-%d %H:%M:%S')}`")
    
    h_col1, h_col2, h_col3 = st.columns([2, 1, 1])
    h_col1.caption(f"접속자: **{user['full_name']}** ({user['username']}) | 권한: **{user['role']}**")
    
    # 메인 상단 즉시 출근/퇴근 버튼
    today_str = tokyo_now.strftime("%Y-%m-%d")
    now_time_str = tokyo_now.strftime("%H:%M:%S")
    
    if h_col2.button("🟢 quick 출근", use_container_width=True):
        try:
            supabase.table("attendance").insert({
                "username": user["username"],
                "full_name": user["full_name"],
                "work_date": today_str,
                "clock_in": now_time_str,
                "work_type": "근무",
                "status": "근무중"
            }).execute()
            st.toast(f"✅ [{now_time_str}] 출근 등록 완료!", icon="🟢")
        except Exception as e:
            st.error(f"출근 기록 실패: {e}")

    if h_col3.button("🔴 quick 퇴근", use_container_width=True):
        try:
            att_check = supabase.table("attendance").select("*").eq("username", user["username"]).eq("work_date", today_str).execute()
            if att_check.data:
                record_id = att_check.data[-1]["id"]
                supabase.table("attendance").update({
                    "clock_out": now_time_str,
                    "status": "퇴근완료"
                }).eq("id", record_id).execute()
                st.toast(f"✅ [{now_time_str}] 퇴근 등록 완료!", icon="🔴")
            else:
                st.warning("오늘 출근 기록이 없습니다.")
        except Exception as e:
            st.error(f"퇴근 기록 실패: {e}")

    st.markdown("---")

    # 사이드바 메뉴 구성
    st.sidebar.title("🏢 ERP Navigation")
    
    menu_list = [
        "📊 대시보드",
        "📋 입/출고 상세 내역 및 수정",
        "📦 입/출고 신규 등록 & 엑셀",
        "🏷️ 상품 마스터 관리",
        "🤝 거래처 마스터",
        "⏰ 타임카드 및 출퇴근/휴무",
        "📅 직원 캘린더"
    ]
    
    if user["role"] == "ADMIN":
        menu_list.append("👥 사용자 가입승인 및 계정관리")
        
    selected_menu = st.sidebar.radio("📌 메뉴 선택", menu_list)
    
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        del st.session_state["user"]
        st.rerun()

    # ---------------------------------------------------------
    # 📊 1. 대시보드
    # ---------------------------------------------------------
    if selected_menu == "📊 대시보드":
        st.title("📊 통합 대시보드")
        
        try:
            # 1) 상품 재고 수량 및 재고 금액(원화 기준: 재고수량 * 상품 매입가)
            prod_res = supabase.table("products").select("*").execute()
            prods = prod_res.data or []
            
            total_stock_qty = sum(p.get("current_stock", 0) for p in prods)
            total_stock_val_krw = sum(p.get("current_stock", 0) * p.get("cost_price_krw", 0) for p in prods)
            
            # 2) 이번 달 입/출고 및 엔화 매출 현황
            first_day = tokyo_now.replace(day=1).strftime("%Y-%m-%d")
            tx_res = supabase.table("inventory_transactions").select("*").gte("transaction_date", first_day).execute()
            tx_data = tx_res.data or []
            
            df_tx = pd.DataFrame(tx_data)
            in_qty = 0
            out_qty = 0
            sales_jpy = 0
            
            if not df_tx.empty:
                in_qty = df_tx[df_tx["transaction_type"] == "IN"]["qty"].sum()
                out_df = df_tx[df_tx["transaction_type"] == "OUT"]
                out_qty = out_df["qty"].sum()
                sales_jpy = out_df["total_price"].sum()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📦 현재 총 잔여 재고량", f"{total_stock_qty:,} 개")
            m2.metric("💰 총 재고 금액 (원화)", f"₩ {total_stock_val_krw:,.0f}")
            m3.metric("🚚 이번 달 출고 수량", f"{out_qty:,} 개")
            m4.metric("💴 이번 달 출고 매출액", f"¥ {sales_jpy:,.0f}")
            
            st.markdown("---")
            st.subheader("📦 상품별 잔여 재고 및 평가액 현황")
            if prods:
                df_p = pd.DataFrame(prods)
                df_p["재고평가액(원화)"] = df_p["current_stock"] * df_p["cost_price_krw"]
                st.dataframe(
                    df_p[["product_code", "product_name", "category", "current_stock", "cost_price_krw", "standard_price_jpy", "재고평가액(원화)"]].rename(
                        columns={
                            "product_code": "상품코드",
                            "product_name": "상품명",
                            "category": "카테고리",
                            "current_stock": "잔여재고",
                            "cost_price_krw": "매입가(₩)",
                            "standard_price_jpy": "판매가(¥)"
                        }
                    ), use_container_width=True
                )
            else:
                st.info("등록된 상품이 없습니다.")
                
        except Exception as e:
            st.error(f"대시보드 로딩 오류: {e}")

    # ---------------------------------------------------------
    # 📋 2. 입/출고 내역 상세 및 수정
    # ---------------------------------------------------------
    elif selected_menu == "📋 입/출고 상세 내역 및 수정":
        st.title("📋 입/출고 내역 상세 및 데이터 수정")
        
        tx_res = supabase.table("inventory_transactions").select("*").order("created_at", desc=True).execute()
        tx_list = tx_res.data or []
        
        if tx_list:
            df_tx_all = pd.DataFrame(tx_list)
            st.dataframe(df_tx_all, use_container_width=True)
            
            st.markdown("---")
            st.subheader("✏️ 특정 트랜잭션 수정 / 삭제")
            
            tx_ids = [f"{t['id']} | [{t['transaction_type']}] {t['product_code']} - {t['client_name']} ({t['qty']}개)" for t in tx_list]
            selected_tx_str = st.selectbox("수정할 내역 선택", tx_ids)
            
            if selected_tx_str:
                selected_id = selected_tx_str.split(" | ")[0]
                curr_tx = next(t for t in tx_list if str(t["id"]) == selected_id)
                
                with st.form("edit_tx_form"):
                    e_type = st.selectbox("구분", ["IN", "OUT"], index=0 if curr_tx["transaction_type"] == "IN" else 1)
                    e_pcode = st.text_input("상품코드", value=curr_tx["product_code"])
                    e_client = st.text_input("거래처명", value=curr_tx["client_name"] or "")
                    e_qty = st.number_input("수량", min_value=1, value=int(curr_tx["qty"]))
                    e_price = st.number_input("단가", min_value=0.0, value=float(curr_tx["unit_price"]))
                    e_notes = st.text_area("비고", value=curr_tx.get("notes", "") or "")
                    
                    e_total = e_qty * e_price
                    st.caption(f"💡 수정 후 총액: {e_total:,.2f}")
                    
                    col_sub1, col_sub2 = st.columns(2)
                    btn_update = col_sub1.form_submit_button("💾 정보 수정 저장")
                    
                    if btn_update:
                        supabase.table("inventory_transactions").update({
                            "transaction_type": e_type,
                            "product_code": e_pcode.strip(),
                            "client_name": e_client.strip(),
                            "qty": e_qty,
                            "unit_price": e_price,
                            "total_price": e_total,
                            "notes": e_notes
                        }).eq("id", selected_id).execute()
                        st.success("내역이 변경되었습니다.")
                        st.rerun()
        else:
            st.info("등록된 입출고 내역이 없습니다.")

    # ---------------------------------------------------------
    # 📦 3. 입/출고 신규 등록 & 엑셀
    # ---------------------------------------------------------
    elif selected_menu == "📦 입/출고 신규 등록 & 엑셀":
        st.title("📦 입/출고 등록")
        
        tab_a, tab_b = st.tabs(["📝 건별 등록", "📂 엑셀 일괄 등록"])
        
        prods = supabase.table("products").select("*").execute().data or []
        clients = supabase.table("clients").select("*").execute().data or []
        
        p_dict = {p["product_code"]: p for p in prods}
        c_dict = {c["client_name"]: c["discount_rate"] for c in clients}
        
        with tab_a:
            with st.form("new_tx_form"):
                tx_type = st.radio("구분", ["IN (입고)", "OUT (출고)"], horizontal=True)
                sel_p = st.selectbox("상품 선택", list(p_dict.keys()) if p_dict else ["등록된 상품 없음"])
                sel_c = st.selectbox("거래처 선택", list(c_dict.keys()) if c_dict else ["등록된 거래처 없음"])
                qty = st.number_input("수량", min_value=1, value=1)
                
                std_price = p_dict.get(sel_p, {}).get("standard_price_jpy", 0) if "OUT" in tx_type else p_dict.get(sel_p, {}).get("cost_price_krw", 0)
                rate = c_dict.get(sel_c, 100.0)
                calc_unit = (std_price * rate) / 100.0
                calc_tot = calc_unit * qty
                
                st.info(f"💡 적용 단가: {calc_unit:,.0f} | **총액: {calc_tot:,.0f}**")
                
                if st.form_submit_button("등록 완료"):
                    code = "IN" if "IN" in tx_type else "OUT"
                    supabase.table("inventory_transactions").insert({
                        "transaction_type": code,
                        "product_code": sel_p,
                        "client_name": sel_c,
                        "qty": qty,
                        "unit_price": calc_unit,
                        "total_price": calc_tot
                    }).execute()
                    
                    # 재고 반영
                    stock_diff = qty if code == "IN" else -qty
                    new_stk = p_dict.get(sel_p, {}).get("current_stock", 0) + stock_diff
                    supabase.table("products").update({"current_stock": new_stk}).eq("product_code", sel_p).execute()
                    
                    st.success("입/출고 등록이 완료되었습니다.")
                    st.rerun()

        with tab_b:
            st.subheader("📂 엑셀 등록 (양식: 구분, 상품코드, 거래처명, 수량)")
            up_file = st.file_uploader("엑셀 파일 선택", type=["xlsx", "csv"])
            if up_file and st.button("업로드 실행"):
                df_up = pd.read_excel(up_file) if up_file.name.endswith(".xlsx") else pd.read_csv(up_file)
                for _, r in df_up.iterrows():
                    code = str(r["구분"]).upper().strip()
                    pcode = str(r["상품코드"]).strip()
                    cname = str(r["거래처명"]).strip()
                    q = int(r["수량"])
                    
                    std = p_dict.get(pcode, {}).get("standard_price_jpy", 0)
                    r_rate = c_dict.get(cname, 100.0)
                    u = (std * r_rate) / 100.0
                    
                    supabase.table("inventory_transactions").insert({
                        "transaction_type": code,
                        "product_code": pcode,
                        "client_name": cname,
                        "qty": q,
                        "unit_price": u,
                        "total_price": u * q
                    }).execute()
                st.success("엑셀 데이터 일괄 업로드 완료!")
                st.rerun()

    # ---------------------------------------------------------
    # 🏷️ 4. 상품 마스터 관리
    # ---------------------------------------------------------
    elif selected_menu == "🏷️ 상품 마스터 관리":
        st.title("🏷️ 상품 마스터 관리")
        
        with st.expander("➕ 신규 상품 등록"):
            with st.form("add_p_form"):
                p_code = st.text_input("상품 코드")
                p_name = st.text_input("상품명")
                p_cat = st.selectbox("카테고리", ["전자기기", "사무용품", "식품", "의류", "기타"])
                p_cost = st.number_input("매입가 (원화 ₩)", min_value=0, value=10000)
                p_price = st.number_input("판매가 (엔화 ¥)", min_value=0, value=1000)
                p_init_stock = st.number_input("초기 재고 수량", min_value=0, value=0)
                
                if st.form_submit_button("상품 저장"):
                    supabase.table("products").insert({
                        "product_code": p_code.strip(),
                        "product_name": p_name.strip(),
                        "category": p_cat,
                        "cost_price_krw": p_cost,
                        "standard_price_jpy": p_price,
                        "current_stock": p_init_stock
                    }).execute()
                    st.success("상품 등록 성공")
                    st.rerun()

        prods = supabase.table("products").select("*").execute().data or []
        if prods:
            st.dataframe(pd.DataFrame(prods), use_container_width=True)

    # ---------------------------------------------------------
    # 🤝 5. 거래처 마스터
    # ---------------------------------------------------------
    elif selected_menu == "🤝 거래처 마스터":
        st.title("🤝 거래처 마스터")
        
        with st.expander("➕ 거래처 등록"):
            with st.form("add_c_form"):
                c_name = st.text_input("거래처명")
                c_type = st.selectbox("구분", ["BUYER", "VENDOR"])
                c_rate = st.number_input("공급가율 (%)", value=100.0)
                
                if st.form_submit_button("저장"):
                    supabase.table("clients").insert({
                        "client_name": c_name.strip(),
                        "client_type": c_type,
                        "discount_rate": c_rate
                    }).execute()
                    st.success("거래처 등록 완료")
                    st.rerun()

        cls = supabase.table("clients").select("*").execute().data or []
        if cls:
            st.dataframe(pd.DataFrame(cls), use_container_width=True)

    # ---------------------------------------------------------
    # ⏰ 6. 타임카드 및 출퇴근/휴무
    # ---------------------------------------------------------
    elif selected_menu == "⏰ 타임카드 및 출퇴근/휴무":
        st.title("⏰ 타임카드 및 근무/휴무 관리")
        
        tab1, tab2 = st.tabs(["👤 내 타임카드", "👥 전체 직원 근태 및 휴무 현황 (관리자)"])
        
        with tab1:
            st.subheader(f"📌 {user['full_name']} 님의 근무 기록")
            
            # 개인 근태 기록
            my_att = supabase.table("attendance").select("*").eq("username", user["username"]).order("work_date", desc=True).execute().data or []
            if my_att:
                st.dataframe(pd.DataFrame(my_att)[["work_date", "clock_in", "clock_out", "work_type", "status"]], use_container_width=True)
            else:
                st.info("출퇴근 기록이 없습니다.")
                
            # 휴가/연차 신청
            with st.expander("📝 휴가/휴무 신청"):
                with st.form("leave_form"):
                    l_date = st.date_input("휴무 희망일", datetime.date.today())
                    l_type = st.selectbox("구분", ["연차", "반차", "휴무", "병가"])
                    if st.form_submit_button("휴무 신청"):
                        supabase.table("attendance").insert({
                            "username": user["username"],
                            "full_name": user["full_name"],
                            "work_date": l_date.strftime("%Y-%m-%d"),
                            "work_type": l_type,
                            "status": "신청완료"
                        }).execute()
                        st.success("휴무가 등록되었습니다.")
                        st.rerun()

        with tab2:
            if user["role"] == "ADMIN":
                st.subheader("👥 전체 직원 근태 현황")
                all_att = supabase.table("attendance").select("*").order("work_date", desc=True).execute().data or []
                if all_att:
                    df_all_att = pd.DataFrame(all_att)
                    
                    # 직원별 필터
                    emp_list = ["전체"] + list(df_all_att["full_name"].unique())
                    selected_emp = st.selectbox("직원 선택", emp_list)
                    
                    if selected_emp != "전체":
                        df_all_att = df_all_att[df_all_att["full_name"] == selected_emp]
                        
                    st.dataframe(df_all_att[["work_date", "full_name", "username", "clock_in", "clock_out", "work_type", "status"]], use_container_width=True)
            else:
                st.warning("전체 조회 권한은 관리자 전용입니다.")

    # ---------------------------------------------------------
    # 📅 7. 직원 캘린더
    # ---------------------------------------------------------
    elif selected_menu == "📅 직원 캘린더":
        st.title("📅 사내 캘린더 및 일정")
        
        with st.form("add_evt"):
            title = st.text_input("일정명")
            e_date = st.date_input("일자", datetime.date.today())
            desc = st.text_area("내용")
            if st.form_submit_button("일정 저장"):
                supabase.table("calendar_events").insert({
                    "title": title,
                    "event_date": e_date.strftime("%Y-%m-%d"),
                    "created_by": user["full_name"],
                    "description": desc
                }).execute()
                st.success("일정 저장 완료")
                st.rerun()

        evts = supabase.table("calendar_events").select("*").order("event_date").execute().data or []
        for ev in evts:
            st.write(f"📅 **[{ev['event_date']}]** {ev['title']} *(작성자: {ev['created_by']})*")
            if ev.get("description"):
                st.caption(f"↳ {ev['description']}")

    # ---------------------------------------------------------
    # 👥 8. 사용자 가입승인 및 계정관리 (ADMIN 전용)
    # ---------------------------------------------------------
    elif selected_menu == "👥 사용자 가입승인 및 계정관리":
        if user["role"] != "ADMIN":
            st.error("접근 권한이 없습니다.")
        else:
            st.title("👥 가입 승인 및 사용자 계정 관리")
            
            # 대기 중 사용자 목록
            pending_users = supabase.table("user_profiles").select("*").eq("status", "PENDING").execute().data or []
            
            st.subheader("⏳ 가입 승인 대기 목록")
            if pending_users:
                for pu in pending_users:
                    col_u1, col_u2, col_u3 = st.columns([3, 1, 1])
                    col_u1.write(f"👤 **{pu['full_name']}** (`{pu['username']}`) | 희망 권한: {pu['role']}")
                    if col_u2.button("✅ 승인", key=f"app_{pu['id']}"):
                        supabase.table("user_profiles").update({"status": "APPROVED"}).eq("id", pu["id"]).execute()
                        st.success(f"{pu['full_name']} 계정 승인 완료!")
                        st.rerun()
                    if col_u3.button("❌ 거절", key=f"rej_{pu['id']}"):
                        supabase.table("user_profiles").update({"status": "REJECTED"}).eq("id", pu["id"]).execute()
                        st.warning(f"{pu['full_name']} 계정 거절 처리")
                        st.rerun()
            else:
                st.info("승인 대기 중인 사용자가 없습니다.")
                
            st.markdown("---")
            st.subheader("📋 전체 승인 사용자 목록")
            all_users = supabase.table("user_profiles").select("id, username, full_name, role, status, is_active, created_at").execute().data or []
            if all_users:
                st.dataframe(pd.DataFrame(all_users), use_container_width=True)
