import streamlit as st
import psycopg2
from psycopg2 import pool
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 페이지 기본 설정 ---
st.set_page_config(
    page_title="GPCLUB JAPAN ERP",
    page_icon="✨",
    layout="wide"
)

# --- 2. 다국어(i18n) 번역 딕셔너리 정의 ---
T = {
    "ko": {
        "title": "✨ GPCLUB JAPAN ERP",
        "login": "🔒 로그인",
        "signup_req": "📝 회원가입 신청",
        "username": "아이디",
        "password": "비밀번호",
        "name": "이름",
        "req_role": "요청 권한",
        "login_btn": "로그인",
        "signup_btn": "가입 신청 제출",
        "login_fail": "아이디/비밀번호가 올바르지 않거나 승인 대기 중인 계정입니다.",
        "signup_exists": "이미 존재하는 아이디입니다.",
        "signup_success": "가입 신청 완료.",
        "logout": "로그아웃",
        "lang_label": "🌐 언어 선택 / Language",
        
        # 메뉴명
        "m_dash": "📊 대시보드 & 잔여재고",
        "m_prod": "📦 취급 제품 마스터",
        "m_in": "📥 입고 등록",
        "m_out": "📤 출고 등록",
        "m_history": "📋 기간별 입출고 이력",
        "m_cust": "🏢 거래처 & 납품단가",
        "m_rate": "🔱 월별 환율 설정",
        "m_user": "👥 계정 관리",

        # 환율 설정
        "rate_title": "🔱 월별 기준 환율 설정 (KRW / JPY)",
        "rate_desc": "한국 매입(원화 ₩)과 일본 매출/비용(엔화 ￥) 간 환산에 사용되는 연월별 기준 환율을 관리합니다.",
        "target_ym": "적용 연-월 (YYYY-MM)",
        "rate_input": "100엔당 원화 환율(₩)",
        "rate_save": "환율 저장",
        "rate_list": "📋 등록된 월별 환율 목록",

        # 대시보드
        "wh_filter": "🏬 창고 필터",
        "rate_info": "💡 적용 환율 ({ym}): 100엔 = {rate_100:,.1f}원 (1엔 = {rate_1:,.2f}원)",
        "tot_qty": "총 재고 수량",
        "tot_krw": "총 재고 원가(원화 ₩)",
        "month_in": "당월 총 입고 수량",
        "month_out": "당월 총 매출액(엔화 ￥)",
        "prod_stock_list": "📋 제품 통합 재고 현황",
        "wh_detail": "🏬 {wh} 창고 상세 (LOT별)",

        # 제품 마스터
        "tab_reg": "➕ 신규 제품 등록",
        "tab_edit": "✏️ 기존 제품 수정 / 삭제",
        "sec_basic": "📌 기본 정보",
        "p_code": "제품 코드*",
        "p_name": "제품명*",
        "p_price_krw": "기본 매입단가(원/KRW ₩)*",
        "sec_jan": "🏷️ JAN 코드",
        "jan_box": "JAN 코드 (곽/소박스)",
        "jan_piece": "JAN 코드 (낱장/단품)",
        "sec_in_box": "📦 박스 입수량",
        "in_box_cnt": "박스 당 곽 수량(개)",
        "in_piece_cnt": "박스 당 낱장 수량(개)",
        "sec_p_size": "📐 곽(제품) 사이즈 (가로 x 세로 x 높이 mm)",
        "sec_c_size": "📦 박스 사이즈 (가로 x 세로 x 높이 mm)",
        "sec_pallet": "🏗️ 1파레트 입수량",
        "pallet_box": "파레트 당 곽 수량(개)",
        "pallet_carton": "파레트 당 박스 수량(개)",
        "btn_save_prod": "제품 마스터 저장",
        "btn_edit_prod": "💾 수정사항 저장",
        "btn_del_prod": "🗑️ 제품 삭제",
        "sel_edit_prod": "수정 또는 삭제할 제품을 선택하세요",

        # 입고
        "in_title": "📥 입고 정보 입력 (한국 매입: 원화 ₩)",
        "in_date": "입고 일자*",
        "in_type": "입고 구분*",
        "sel_master": "취급 제품 선택 (선택 시 자동입력)",
        "direct_input": "직접 입력",
        "lot_no": "LOT 번호*",
        "warehouse": "입고 창고*",
        "in_qty": "입고 수량*",
        "in_price": "매입 단가(원/KRW ₩)*",
        "btn_in_confirm": "입고 확정",

        # 출고
        "out_title": "📤 출고 등록 (납품/FOC/샘플)",
        "out_date": "출고 일자*",
        "out_category": "출고 구분*",
        "out_wh": "출고 창고*",
        "cust_name": "발주 거래처명*",
        "sel_item": "출고 품목*",
        "sel_lot": "LOT 번호*",
        "out_qty": "출고 수량*",
        "out_unit_price": "적용 단가",
        "foc_notice": "💡 FOC/샘플건은 매출 단가 ￥0으로 처리되며, 원가(원화 ₩{cost:,.0f})로 이력이 집계됩니다.",
        "sec_ship": "🚚 납품처 정보 (배송지)",
        "po_num": "발주 번호",
        "del_place": "납품처 회사명*",
        "del_phone": "전화번호*",
        "zip_code": "우편번호*",
        "del_addr": "상세 주소*",
        "ship_fee": "배송비(엔/JPY ￥)",
        "btn_out_confirm": "출고 확정 및 재고 차감",

        # 거래처
        "add_cust_title": "➕ 신규 거래처 추가",
        "new_cust_name": "새 거래처명",
        "btn_add_cust": "거래처 추가",
        "sel_cust_mgt": "🏢 관리할 거래처 선택",
        "price_reg_title": "➕ {cust} 신규 품목 납품 단가 등록 (엔화 ￥)",
        "price_jpy": "납품 단가(엔/JPY ￥)*",
        "btn_add_price": "신규 단가 등록",
        "price_list_title": "📋 {cust} 등록된 품목 단가 목록 (수정/삭제)"
    },
    "ja": {
        "title": "✨ GPCLUB JAPAN ERP",
        "login": "🔒 ログイン",
        "signup_req": "📝 新規会員登録",
        "username": "ユーザーID",
        "password": "パスワード",
        "name": "氏名",
        "req_role": "申請権限",
        "login_btn": "ログイン",
        "signup_btn": "登録申請を送信",
        "login_fail": "ID/パスワード가 正しくないか、承認待ちのアカウントです。",
        "signup_exists": "既に存在するユーザーIDです。",
        "signup_success": "登録申請が完了しました。",
        "logout": "ログアウト",
        "lang_label": "🌐 言語選択 / Language",

        # 메뉴명
        "m_dash": "📊 ダッシュボード & 在庫",
        "m_prod": "📦 取扱商品マスター",
        "m_in": "📥 入庫登録 (ウォン ₩)",
        "m_out": "📤 出庫登録 (納品/FOC/サンプル)",
        "m_history": "📋 期間別入出庫履歴",
        "m_cust": "🏢 取引先 & 納品単価(円 ￥)",
        "m_rate": "🔱 月別為替レート設定",
        "m_user": "👥 アカウント管理",

        # 환율 설정
        "rate_title": "🔱 月別基準為替レート設定 (KRW / JPY)",
        "rate_desc": "韓国仕入(ウォン ₩)と日本売上/費用(円 ￥)の換算に使用される年月別の基準レートを管理します。",
        "target_ym": "適用年月 (YYYY-MM)",
        "rate_input": "100円あたりのウォンレート(₩)",
        "rate_save": "レート保存",
        "rate_list": "📋 登録済み月別レート一覧",

        # 대시보드
        "wh_filter": "🏬 倉庫フィルター",
        "rate_info": "💡 適用レート ({ym}): 100円 = {rate_100:,.1f}ウォン (1円 = {rate_1:,.2f}ウォン)",
        "tot_qty": "総在庫数量",
        "tot_krw": "総在庫原価(ウォン ₩)",
        "month_in": "当月 総入庫数量",
        "month_out": "当月 総売上高(円 ￥)",
        "prod_stock_list": "📋 商品統合在庫現況",
        "wh_detail": "🏬 {wh} 倉庫詳細 (LOT別)",

        # 제품 마스터
        "tab_reg": "➕ 新規商品登録",
        "tab_edit": "✏️ 既存商品修正 / 削除",
        "sec_basic": "📌 基本情報",
        "p_code": "商品コード*",
        "p_name": "商品名*",
        "p_price_krw": "基本仕入単価(ウォン/KRW ₩)*",
        "sec_jan": "🏷️ JANコード",
        "jan_box": "JANコード (箱/小箱)",
        "jan_piece": "JANコード (単品/バラ)",
        "sec_in_box": "📦 ケース入数",
        "in_box_cnt": "ケース内箱数",
        "in_piece_cnt": "ケース内バラ数",
        "sec_p_size": "📐 箱(商品)サイズ (幅 x 奥行 x 高さ mm)",
        "sec_c_size": "📦 外箱サイズ (幅 x 奥行 x 高さ mm)",
        "sec_pallet": "🏗️ 1パレット入数",
        "pallet_box": "パレット内箱数",
        "pallet_carton": "パレット内外箱数",
        "btn_save_prod": "商品マスター保存",
        "btn_edit_prod": "💾 修正事項を保存",
        "btn_del_prod": "🗑️ 商品削除",
        "sel_edit_prod": "修正または削除する商品を選択してください",

        # 입고
        "in_title": "📥 入庫情報入力 (韓国仕入: ウォン ₩)",
        "in_date": "入庫日*",
        "in_type": "入庫区分*",
        "sel_master": "取扱商品選択 (選択時自動入力)",
        "direct_input": "Direct Input / 直接入力",
        "lot_no": "LOT番号*",
        "warehouse": "入庫倉庫*",
        "in_qty": "入庫数量*",
        "in_price": "仕入単価(ウォン/KRW ₩)*",
        "btn_in_confirm": "入庫確定",

        # 출고
        "out_title": "📤 出庫登録 (納品/FOC/サンプル)",
        "out_date": "出荷日*",
        "out_category": "出荷区分*",
        "out_wh": "出荷倉庫*",
        "cust_name": "発注取引先名*",
        "sel_item": "出荷品目*",
        "sel_lot": "LOT番号*",
        "out_qty": "出荷数量*",
        "out_unit_price": "適用単価",
        "foc_notice": "💡 FOC/サンプルは売上単価 ￥0として処理され、原価(ウォン ₩{cost:,.0f})で履歴が集計されます。",
        "sec_ship": "🚚 納品先情報 (配送先)",
        "po_num": "発注番号",
        "del_place": "納品先 会社名*",
        "del_phone": "電話番号*",
        "zip_code": "郵便番号*",
        "del_addr": "詳細住所*",
        "ship_fee": "送料(円/JPY ￥)",
        "btn_out_confirm": "出荷確定および在庫減算",

        # 거래처
        "add_cust_title": "➕ 新規取引先追加",
        "new_cust_name": "新しい取引先名",
        "btn_add_cust": "取引先追加",
        "sel_cust_mgt": "🏢 管理する取引先を選択",
        "price_reg_title": "➕ {cust} 新規品目納品単価登録 (円 ￥)",
        "price_jpy": "納品単価(円/JPY ￥)*",
        "btn_add_price": "新規単価登録",
        "price_list_title": "📋 {cust} 登録済み単価一覧 (修正/削除)"
    },
    "en": {
        "title": "✨ GPCLUB JAPAN ERP",
        "login": "🔒 Login",
        "signup_req": "📝 Request Account",
        "username": "Username",
        "password": "Password",
        "name": "Full Name",
        "req_role": "Requested Role",
        "login_btn": "Log In",
        "signup_btn": "Submit Application",
        "login_fail": "Invalid credentials or account pending approval.",
        "signup_exists": "Username already exists.",
        "signup_success": "Application submitted successfully.",
        "logout": "Log Out",
        "lang_label": "🌐 Language Selection",

        # 메뉴명
        "m_dash": "📊 Dashboard & Inventory",
        "m_prod": "📦 Product Master",
        "m_in": "📥 Inbound Entry (KRW ₩)",
        "m_out": "📤 Outbound Entry (Sales/FOC/Sample)",
        "m_history": "📋 History Logs",
        "m_cust": "🏢 Customer & Price (JPY ￥)",
        "m_rate": "🔱 Monthly Exchange Rates",
        "m_user": "👥 User Management",

        # 환율 설정
        "rate_title": "🔱 Monthly Exchange Rate Settings (KRW / JPY)",
        "rate_desc": "Manage conversion exchange rates between Purchase in Korea (KRW ₩) and Sales in Japan (JPY ￥).",
        "target_ym": "Target Month (YYYY-MM)",
        "rate_input": "KRW Rate per 100 JPY (₩)",
        "rate_save": "Save Exchange Rate",
        "rate_list": "📋 Registered Exchange Rates List",

        # 대시보드
        "wh_filter": "🏬 Warehouse Filter",
        "rate_info": "💡 Exchange Rate ({ym}): 100 JPY = {rate_100:,.1f} KRW (1 JPY = {rate_1:,.2f} KRW)",
        "tot_qty": "Total Stock Qty",
        "tot_krw": "Total Cost (KRW ₩)",
        "month_in": "Monthly Inbound Qty",
        "month_out": "Monthly Sales (JPY ￥)",
        "prod_stock_list": "📋 Consolidated Inventory Status",
        "wh_detail": "🏬 {wh} Warehouse Details (by LOT)",

        # 제품 마스터
        "tab_reg": "➕ New Product Registration",
        "tab_edit": "✏️ Edit / Delete Existing Product",
        "sec_basic": "📌 Basic Information",
        "p_code": "Product Code*",
        "p_name": "Product Name*",
        "p_price_krw": "Default Purchase Price (KRW ₩)*",
        "sec_jan": "🏷️ JAN Codes",
        "jan_box": "JAN Code (Inner Box)",
        "jan_piece": "JAN Code (Piece/Single)",
        "sec_in_box": "📦 Carton Capacity",
        "in_box_cnt": "Boxes per Carton",
        "in_piece_cnt": "Pieces per Carton",
        "sec_p_size": "📐 Inner Box Dimensions (W x D x H mm)",
        "sec_c_size": "📦 Outer Carton Dimensions (W x D x H mm)",
        "sec_pallet": "🏗️ Pallet Capacity",
        "pallet_box": "Inner Boxes per Pallet",
        "pallet_carton": "Outer Cartons per Pallet",
        "btn_save_prod": "Save Product Master",
        "btn_edit_prod": "💾 Save Changes",
        "btn_del_prod": "🗑️ Delete Product",
        "sel_edit_prod": "Select product to edit or delete",

        # 입고
        "in_title": "📥 Inbound Registration (Korea Purchase: KRW ₩)",
        "in_date": "Inbound Date*",
        "in_type": "Inbound Category*",
        "sel_master": "Select Product (Auto-fill)",
        "direct_input": "Direct Input",
        "lot_no": "LOT Number*",
        "warehouse": "Warehouse*",
        "in_qty": "Quantity*",
        "in_price": "Unit Cost (KRW ₩)*",
        "btn_in_confirm": "Confirm Inbound",

        # 출고
        "out_title": "📤 Outbound Registration (Japan Sales/Provide)",
        "out_date": "Outbound Date*",
        "out_category": "Outbound Category*",
        "out_wh": "Source Warehouse*",
        "cust_name": "Customer Name*",
        "sel_item": "Outbound Item*",
        "sel_lot": "LOT Number*",
        "out_qty": "Quantity*",
        "out_unit_price": "Applied Price",
        "foc_notice": "💡 FOC/Sample items are billed at ￥0 sales, tracked by cost price (KRW ₩{cost:,.0f}).",
        "sec_ship": "🚚 Delivery Address Details",
        "po_num": "PO Number",
        "del_place": "Delivery Company Name*",
        "del_phone": "Phone Number*",
        "zip_code": "Postal Code*",
        "del_addr": "Full Address*",
        "ship_fee": "Shipping Fee (JPY ￥)",
        "btn_out_confirm": "Confirm Outbound & Deduct Stock",

        # 거래처
        "add_cust_title": "➕ Add New Customer",
        "new_cust_name": "Customer Name",
        "btn_add_cust": "Add Customer",
        "sel_cust_mgt": "🏢 Select Customer to Manage",
        "price_reg_title": "➕ {cust} Register New Delivery Price (JPY ￥)",
        "price_jpy": "Delivery Price (JPY ￥)*",
        "btn_add_price": "Register Price",
        "price_list_title": "📋 {cust} Item Price List (Edit/Delete)"
    }
}

# --- 3. DB 연결 커넥션 풀(Connection Pool) 최적화 ---
@st.cache_resource
def init_db_pool():
    try:
        return pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=st.secrets.get("DB_HOST"),
            database=st.secrets.get("DB_NAME", "postgres"),
            user=st.secrets.get("DB_USER"),
            password=st.secrets.get("DB_PASSWORD"),
            port=st.secrets.get("DB_PORT", "6543")
        )
    except Exception as e:
        st.error(f"DB Connection Pool Error: {e}")
        return None

db_pool = init_db_pool()

def get_connection():
    if db_pool:
        return db_pool.getconn()
    return None

def release_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def run_query(query, params=None):
    conn = get_connection()
    if conn is None: return []
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
            return []
    except Exception as e:
        st.error(f"Query Error: {e}")
        return []
    finally:
        release_connection(conn)

def run_commit(query, params=None):
    conn = get_connection()
    if conn is None: return False
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
        st.cache_data.clear() # 데이터 변경 시 캐시 자동 초기화
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False
    finally:
        release_connection(conn)

# --- 4. 자주 쓰이는 조회 쿼리 캐싱(st.cache_data) ---
@st.cache_data(ttl=60)
def get_exchange_rate(year_month=None):
    if not year_month:
        year_month = datetime.now().strftime('%Y-%m')
    res = run_query("SELECT krw_per_jpy FROM exchange_rates WHERE year_month=%s;", (year_month,))
    if res and res[0]['krw_per_jpy']:
        return float(res[0]['krw_per_jpy'])
    return 9.0

@st.cache_data(ttl=60)
def fetch_master_products():
    return run_query("SELECT * FROM master_products ORDER BY item_name;")

@st.cache_data(ttl=60)
def fetch_customers():
    return run_query("SELECT customer_name FROM customers ORDER BY customer_name;")

@st.cache_data(ttl=60)
def fetch_customer_prices(customer_name):
    return run_query("SELECT * FROM customer_prices WHERE customer_name=%s ORDER BY item_name;", (customer_name,))

# --- 5. 세션 상태 및 언어 설정 초기화 ---
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": "", "role": "guest"})

if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"

lang_map = {"한국어 🇰🇷": "ko", "日本語 🇯🇵": "ja", "English 🇺🇸": "en"}
selected_lang_label = st.sidebar.selectbox(
    "🌐 Language / 언어",
    options=list(lang_map.keys()),
    index=list(lang_map.values()).index(st.session_state["lang"])
)
st.session_state["lang"] = lang_map[selected_lang_label]
L = T[st.session_state["lang"]]

# --- 6. 로그인 및 회원가입 화면 ---
if not st.session_state["logged_in"]:
    st.title(L["title"])
    tab1, tab2 = st.tabs([L["login"], L["signup_req"]])
    
    with tab1:
        username_input = st.text_input(L["username"])
        password_input = st.text_input(L["password"], type="password")
        if st.button(L["login_btn"], use_container_width=True):
            user = run_query("SELECT * FROM users WHERE username=%s AND password=%s AND status='active';", (username_input, password_input))
            if user:
                st.session_state.update({"logged_in": True, "username": user[0]['username'], "role": user[0].get('role', 'staff')})
                st.rerun()
            else:
                st.error(L["login_fail"])

    with tab2:
        new_user = st.text_input(L["username"], key="su_user")
        new_pass = st.text_input(L["password"], type="password", key="su_pass")
        new_name = st.text_input(L["name"])
        req_role = {"사원": "staff", "관리자": "admin", "방문자": "guest"}[st.selectbox(L["req_role"], ["사원", "관리자", "방문자"])]
        if st.button(L["signup_btn"]):
            if new_user and new_pass:
                if run_query("SELECT * FROM users WHERE username=%s;", (new_user,)):
                    st.warning(L["signup_exists"])
                elif run_commit("INSERT INTO users (username, password, name, role, status) VALUES (%s, %s, %s, %s, 'pending');", (new_user, new_pass, new_name, req_role)):
                    st.success(L["signup_success"])

# --- 7. 메인 ERP 화면 ---
else:
    role = st.session_state["role"]
    warehouses = ["SAGAWA", "L&K", "大吉商事"]
    
    st.sidebar.title("✨ GPCLUB JAPAN")
    
    menu_keys = [
        ("m_dash", L["m_dash"]),
        ("m_prod", L["m_prod"]),
        ("m_in", L["m_in"]),
        ("m_out", L["m_out"]),
        ("m_history", L["m_history"]),
        ("m_cust", L["m_cust"]),
        ("m_rate", L["m_rate"])
    ]
    if role == "admin":
        menu_keys.append(("m_user", L["m_user"]))
        
    menu_labels = [m[1] for m in menu_keys]
    selected_menu_label = st.sidebar.radio("Menu", menu_labels)
    selected_menu_key = [m[0] for m in menu_keys if m[1] == selected_menu_label][0]

    if st.sidebar.button(L["logout"]):
        st.session_state.update({"logged_in": False, "username": "", "role": "guest"})
        st.rerun()

    st.title(f"{selected_menu_label}")

    # --- 🔱 월별 환율 설정 ---
    if selected_menu_key == "m_rate":
        st.subheader(L["rate_title"])
        st.caption(L["rate_desc"])

        curr_ym = datetime.now().strftime('%Y-%m')
        col_ym, col_rate = st.columns(2)
        target_ym = col_ym.text_input(L["target_ym"], value=curr_ym)
        
        current_rate = get_exchange_rate(target_ym)
        rate_100jpy = col_rate.number_input(L["rate_input"], value=float(current_rate * 100), step=10.0)
        
        if st.button(L["rate_save"], type="primary"):
            rate_per_jpy = rate_100jpy / 100.0
            if run_commit("""
                INSERT INTO exchange_rates (year_month, krw_per_jpy) 
                VALUES (%s, %s) 
                ON CONFLICT (year_month) DO UPDATE SET krw_per_jpy=EXCLUDED.krw_per_jpy, updated_at=CURRENT_TIMESTAMP;
            """, (target_ym, rate_per_jpy)):
                st.success(f"Saved: {target_ym} (100 JPY = {rate_100jpy:,.1f} KRW)")
                st.rerun()

        st.divider()
        st.markdown(f"##### {L['rate_list']}")
        rates_df = run_query("SELECT year_month as \"YM\", (krw_per_jpy * 100) as \"KRW/100JPY\", krw_per_jpy as \"KRW/1JPY\", updated_at as \"Updated\" FROM exchange_rates ORDER BY year_month DESC;")
        if rates_df:
            st.dataframe(pd.DataFrame(rates_df), use_container_width=True)

    # --- 📊 대시보드 ---
    elif selected_menu_key == "m_dash":
        current_month = datetime.now().strftime('%Y-%m')
        
        f_col1, f_col2 = st.columns(2)
        wh_filter = f_col1.selectbox(L["wh_filter"], ["ALL"] + warehouses)
        selected_ym = f_col2.text_input(L["target_ym"], value=current_month)

        applied_rate = get_exchange_rate(selected_ym)
        st.info(L["rate_info"].format(ym=selected_ym, rate_100=applied_rate*100, rate_1=applied_rate))

        if wh_filter == "ALL":
            total_qty = run_query("SELECT SUM(quantity) as v FROM inventory;")[0]['v'] or 0
            total_amt_krw = run_query("SELECT SUM(quantity * purchase_price) as v FROM inventory;")[0]['v'] or 0
            total_amt_jpy = total_amt_krw / applied_rate if applied_rate > 0 else 0

            month_in = run_query("SELECT SUM(quantity) as v FROM stock_movements WHERE movement_type='IN' AND TO_CHAR(movement_date, 'YYYY-MM')=%s;", (selected_ym,))[0]['v'] or 0
            month_out_jpy = run_query("SELECT SUM(total_amount) as v FROM stock_movements WHERE movement_type='OUT' AND transaction_type='납품(유상)' AND TO_CHAR(movement_date, 'YYYY-MM')=%s;", (selected_ym,))[0]['v'] or 0

            k1, k2, k3, k4 = st.columns(4)
            k1.metric(L["tot_qty"], f"{total_qty:,}")
            k2.metric(L["tot_krw"], f"₩{total_amt_krw:,.0f}", help=f"JPY: ￥{total_amt_jpy:,.0f}")
            k3.metric(L["month_in"], f"{month_in:,}")
            k4.metric(L["month_out"], f"￥{month_out_jpy:,.0f}", help=f"KRW: ₩{month_out_jpy * applied_rate:,.0f}")

            st.subheader(L["prod_stock_list"])
            df = run_query("SELECT item_name, jan_box, SUM(quantity) as qty, AVG(purchase_price) as avg_p_krw, SUM(quantity * purchase_price) as tot_krw FROM inventory GROUP BY item_name, jan_box ORDER BY item_name;")
            if df:
                df_pd = pd.DataFrame(df)
                df_pd['tot_jpy'] = df_pd['tot_krw'] / applied_rate if applied_rate > 0 else 0
                st.dataframe(df_pd, use_container_width=True)
        else:
            st.subheader(L["wh_detail"].format(wh=wh_filter))
            df = run_query("SELECT item_code, item_name, lot_no, quantity, purchase_price, (quantity*purchase_price) as tot_krw FROM inventory WHERE warehouse=%s;", (wh_filter,))
            if df:
                df_pd = pd.DataFrame(df)
                df_pd['tot_jpy'] = df_pd['tot_krw'] / applied_rate if applied_rate > 0 else 0
                st.dataframe(df_pd, use_container_width=True)

    # --- 📦 취급 제품 마스터 ---
    elif selected_menu_key == "m_prod" and role != "guest":
        tab_reg, tab_edit = st.tabs([L["tab_reg"], L["tab_edit"]])

        with tab_reg:
            st.subheader(L["tab_reg"])
            with st.form("master_product_form", clear_on_submit=False):
                st.markdown(f"##### {L['sec_basic']}")
                c1, c2, c3 = st.columns(3)
                m_code = c1.text_input(L["p_code"])
                m_name = c2.text_input(L["p_name"])
                m_price = c3.number_input(L["p_price_krw"], value=0.0, step=100.0)

                st.markdown(f"##### {L['sec_jan']}")
                j1, j2 = st.columns(2)
                m_jan_box = j1.text_input(L["jan_box"])
                m_jan_piece = j2.text_input(L["jan_piece"])

                st.markdown(f"##### {L['sec_in_box']}")
                b1, b2 = st.columns(2)
                m_box_in_box = b1.number_input(L["in_box_cnt"], min_value=0, value=0)
                m_box_in_piece = b2.number_input(L["in_piece_cnt"], min_value=0, value=0)

                st.markdown(f"##### {L['sec_p_size']}")
                ps1, ps2, ps3 = st.columns(3)
                m_ps_w = ps1.number_input("W", min_value=0.0, value=0.0, step=1.0, key="pw")
                m_ps_d = ps2.number_input("D", min_value=0.0, value=0.0, step=1.0, key="pd")
                m_ps_h = ps3.number_input("H", min_value=0.0, value=0.0, step=1.0, key="ph")

                st.markdown(f"##### {L['sec_c_size']}")
                cs1, cs2, cs3 = st.columns(3)
                m_cs_w = cs1.number_input("W", min_value=0.0, value=0.0, step=1.0, key="cw")
                m_cs_d = cs2.number_input("D", min_value=0.0, value=0.0, step=1.0, key="cd")
                m_cs_h = cs3.number_input("H", min_value=0.0, value=0.0, step=1.0, key="ch")

                st.markdown(f"##### {L['sec_pallet']}")
                pl1, pl2 = st.columns(2)
                m_pallet_box = pl1.number_input(L["pallet_box"], min_value=0, value=0)
                m_pallet_carton = pl2.number_input(L["pallet_carton"], min_value=0, value=0)

                submitted = st.form_submit_button(L["btn_save_prod"], type="primary", use_container_width=True)

                if submitted:
                    if m_code and m_name:
                        sql = """
                        INSERT INTO master_products (
                            item_code, item_name, default_purchase_price,
                            jan_box, jan_piece, box_in_box, box_in_piece,
                            prod_size_w, prod_size_d, prod_size_h,
                            carton_size_w, carton_size_d, carton_size_h,
                            pallet_in_box, pallet_in_carton
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (item_code) DO UPDATE SET
                            item_name=EXCLUDED.item_name, default_purchase_price=EXCLUDED.default_purchase_price,
                            jan_box=EXCLUDED.jan_box, jan_piece=EXCLUDED.jan_piece,
                            box_in_box=EXCLUDED.box_in_box, box_in_piece=EXCLUDED.box_in_piece,
                            prod_size_w=EXCLUDED.prod_size_w, prod_size_d=EXCLUDED.prod_size_d, prod_size_h=EXCLUDED.prod_size_h,
                            carton_size_w=EXCLUDED.carton_size_w, carton_size_d=EXCLUDED.carton_size_d, carton_size_h=EXCLUDED.carton_size_h,
                            pallet_in_box=EXCLUDED.pallet_in_box, pallet_in_carton=EXCLUDED.pallet_in_carton;
                        """
                        params = (
                            m_code, m_name, m_price, m_jan_box, m_jan_piece,
                            m_box_in_box, m_box_in_piece, m_ps_w, m_ps_d, m_ps_h,
                            m_cs_w, m_cs_d, m_cs_h, m_pallet_box, m_pallet_carton
                        )
                        if run_commit(sql, params):
                            st.success("Saved.")
                            st.rerun()

        with tab_edit:
            st.subheader(L["tab_edit"])
            all_products = fetch_master_products()
            
            if all_products:
                prod_map = {f"{p['item_name']} [{p['item_code']}]": p for p in all_products}
                selected_label = st.selectbox(L["sel_edit_prod"], list(prod_map.keys()))
                curr_p = prod_map[selected_label]

                st.divider()
                with st.form("master_product_edit_form"):
                    st.markdown(f"##### {L['sec_basic']}")
                    ec1, ec2, ec3 = st.columns(3)
                    e_code = ec1.text_input(L["p_code"], value=curr_p['item_code'], disabled=True)
                    e_name = ec2.text_input(L["p_name"], value=curr_p['item_name'] or "")
                    e_price = ec3.number_input(L["p_price_krw"], value=float(curr_p['default_purchase_price'] or 0.0), step=100.0)

                    st.markdown(f"##### {L['sec_jan']}")
                    ej1, ej2 = st.columns(2)
                    e_jan_box = ej1.text_input(L["jan_box"], value=curr_p.get('jan_box') or "")
                    e_jan_piece = ej2.text_input(L["jan_piece"], value=curr_p.get('jan_piece') or "")

                    st.markdown(f"##### {L['sec_in_box']}")
                    eb1, eb2 = st.columns(2)
                    e_box_in_box = eb1.number_input(L["in_box_cnt"], min_value=0, value=int(curr_p.get('box_in_box') or 0))
                    e_box_in_piece = eb2.number_input(L["in_piece_cnt"], min_value=0, value=int(curr_p.get('box_in_piece') or 0))

                    st.markdown(f"##### {L['sec_p_size']}")
                    eps1, eps2, eps3 = st.columns(3)
                    e_ps_w = eps1.number_input("W", min_value=0.0, value=float(curr_p.get('prod_size_w') or 0.0), step=1.0, key="epw")
                    e_ps_d = eps2.number_input("D", min_value=0.0, value=float(curr_p.get('prod_size_d') or 0.0), step=1.0, key="epd")
                    e_ps_h = eps3.number_input("H", min_value=0.0, value=float(curr_p.get('prod_size_h') or 0.0), step=1.0, key="eph")

                    st.markdown(f"##### {L['sec_c_size']}")
                    ecs1, ecs2, ecs3 = st.columns(3)
                    e_cs_w = ecs1.number_input("W", min_value=0.0, value=float(curr_p.get('carton_size_w') or 0.0), step=1.0, key="ecw")
                    e_cs_d = ecs2.number_input("D", min_value=0.0, value=float(curr_p.get('carton_size_d') or 0.0), step=1.0, key="ecd")
                    e_cs_h = ecs3.number_input("H", min_value=0.0, value=float(curr_p.get('carton_size_h') or 0.0), step=1.0, key="ech")

                    st.markdown(f"##### {L['sec_pallet']}")
                    epl1, epl2 = st.columns(2)
                    e_pallet_box = epl1.number_input(L["pallet_box"], min_value=0, value=int(curr_p.get('pallet_in_box') or 0))
                    e_pallet_carton = epl2.number_input(L["pallet_carton"], min_value=0, value=int(curr_p.get('pallet_in_carton') or 0))

                    btn_col1, btn_col2 = st.columns([1, 1])
                    edit_submitted = btn_col1.form_submit_button(L["btn_edit_prod"], type="primary", use_container_width=True)
                    delete_submitted = btn_col2.form_submit_button(L["btn_del_prod"], type="secondary", use_container_width=True)

                    if edit_submitted and e_name:
                        update_sql = """
                        UPDATE master_products SET
                            item_name=%s, default_purchase_price=%s,
                            jan_box=%s, jan_piece=%s, box_in_box=%s, box_in_piece=%s,
                            prod_size_w=%s, prod_size_d=%s, prod_size_h=%s,
                            carton_size_w=%s, carton_size_d=%s, carton_size_h=%s,
                            pallet_in_box=%s, pallet_in_carton=%s
                        WHERE item_code=%s;
                        """
                        update_params = (
                            e_name, e_price, e_jan_box, e_jan_piece, e_box_in_box, e_box_in_piece,
                            e_ps_w, e_ps_d, e_ps_h, e_cs_w, e_cs_d, e_cs_h,
                            e_pallet_box, e_pallet_carton, e_code
                        )
                        if run_commit(update_sql, update_params):
                            st.success("Updated.")
                            st.rerun()

                    if delete_submitted:
                        if run_commit("DELETE FROM master_products WHERE item_code=%s;", (e_code,)):
                            st.warning("Deleted.")
                            st.rerun()

        st.divider()
        master_list = fetch_master_products()
        if master_list:
            st.dataframe(pd.DataFrame(master_list), use_container_width=True)

    # --- 📥 입고 등록 (한국 매입: 원화 ₩) ---
    elif selected_menu_key == "m_in" and role != "guest":
        master_products = fetch_master_products()
        prod_options = {f"{p['item_name']} [{p['item_code']}]": p for p in master_products} if master_products else {}
        
        st.subheader(L["in_title"])
        col1, col2, col3 = st.columns(3)
        with col1:
            in_date = st.date_input(L["in_date"], datetime.today())
            in_type = st.selectbox(L["in_type"], ["매입입고", "기타입고"])
            
            selected_master = st.selectbox(L["sel_master"], [L["direct_input"]] + list(prod_options.keys()))
            if selected_master != L["direct_input"]:
                p_data = prod_options[selected_master]
                in_code = st.text_input(L["p_code"], value=p_data['item_code'])
                in_name = st.text_input(L["p_name"], value=p_data['item_name'])
                in_jan = st.text_input(L["jan_box"], value=p_data['jan_box'] or "")
                default_price = float(p_data['default_purchase_price'] or 0.0)
            else:
                in_code = st.text_input(L["p_code"])
                in_name = st.text_input(L["p_name"])
                in_jan = st.text_input(L["jan_box"])
                default_price = 0.0

        with col2:
            in_lot = st.text_input(L["lot_no"])
            in_wh = st.selectbox(L["warehouse"], warehouses)
        with col3:
            in_qty = st.number_input(L["in_qty"], min_value=1)
            in_price = st.number_input(L["in_price"], value=default_price)

        if st.button(L["btn_in_confirm"], type="primary"):
            if in_code and in_name and in_lot:
                ex = run_query("SELECT id, quantity FROM inventory WHERE item_code=%s AND lot_no=%s AND warehouse=%s;", (in_code, in_lot, in_wh))
                if ex: run_commit("UPDATE inventory SET quantity=%s, purchase_price=%s WHERE id=%s;", (ex[0]['quantity']+in_qty, in_price, ex[0]['id']))
                else: run_commit("INSERT INTO inventory (item_code, item_name, jan_code, lot_no, warehouse, quantity, purchase_price) VALUES (%s, %s, %s, %s, %s, %s, %s);", (in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price))
                
                run_commit("INSERT INTO stock_movements (movement_date, movement_type, transaction_type, item_code, item_name, jan_code, lot_no, warehouse, quantity, unit_price, total_amount) VALUES (%s, 'IN', %s, %s, %s, %s, %s, %s, %s, %s, %s);", 
                           (in_date, in_type, in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price, in_qty*in_price))
                st.success("Confirmed.")
                st.rerun()

    # --- 📤 출고 등록 ---
    elif selected_menu_key == "m_out" and role != "guest":
        st.subheader(L["out_title"])
        
        st.markdown("##### 📌 출고 기본 정보")
        c1, c2, c3 = st.columns(3)
        out_date = c1.date_input(L["out_date"], datetime.today())
        out_trans = c2.selectbox(L["out_category"], ["납품(유상)", "FOC(무상)", "샘플발송"])
        out_wh = c3.selectbox(L["out_wh"], warehouses)

        st.markdown("##### 📦 거래처 / 품목 / 수량 선택")
        c_col1, c_col2 = st.columns(2)
        
        cust_list = [c['customer_name'] for c in fetch_customers()]
        selected_cust = c_col1.selectbox(L["cust_name"], cust_list) if cust_list else c_col1.text_input(L["cust_name"])

        if selected_cust:
            cust_items = fetch_customer_prices(selected_cust)
            if cust_items:
                items_map = {f"{i['item_name']} [코드:{i['item_code']}] (납품단가: ￥{i['delivery_price']})": i for i in cust_items}
            else:
                all_p = fetch_master_products()
                items_map = {f"{i['item_name']} [{i['item_code']}]": i for i in all_p} if all_p else {}

            selected_item_label = c_col2.selectbox(L["sel_item"], list(items_map.keys())) if items_map else None

            if selected_item_label:
                sel_item = items_map[selected_item_label]
                item_code = sel_item['item_code']
                item_name = sel_item['item_name']
                cust_jpy_price = float(sel_item.get('delivery_price', 0.0))

                q_col1, q_col2, q_col3 = st.columns(3)
                lots = {f"LOT: {l['lot_no']} (잔여재고: {l['quantity']}개, 매입단가: ₩{l['purchase_price']:,.0f})": l for l in run_query("SELECT * FROM inventory WHERE item_code=%s AND warehouse=%s AND quantity>0;", (item_code, out_wh))}

                if lots:
                    sel_lot = lots[q_col1.selectbox(L["sel_lot"], list(lots.keys()))]
                    out_qty = q_col2.number_input(L["out_qty"], min_value=1, max_value=sel_lot['quantity'], value=1)

                    cost_krw = float(sel_lot['purchase_price'] or 0.0)
                    if out_trans == "납품(유상)":
                        price_jpy = cust_jpy_price
                        total_amount = out_qty * price_jpy
                        q_col3.metric("적용 단가 / 총액", f"￥{price_jpy:,.0f}", f"총 ￥{total_amount:,.0f}")
                    else:
                        price_jpy = 0.0
                        total_amount = 0.0
                        q_col3.info(L["foc_notice"].format(cost=cost_krw))

                    st.divider()
                    st.markdown(f"##### {L['sec_ship']}")
                    
                    s1, s2, s3 = st.columns(3)
                    po_num = s1.text_input(L["po_num"])
                    del_place = s2.text_input(L["del_place"], placeholder="예: (주)일본유통 도쿄지점")
                    del_phone = s3.text_input(L["del_phone"], placeholder="예: 03-1234-5678")

                    z1, z2, z3 = st.columns([1, 2.5, 1])
                    zip_code = z1.text_input(L["zip_code"], placeholder="123-4567")
                    del_addr = z2.text_input(L["del_addr"], placeholder="도쿄도 미나토쿠 ...")
                    ship_fee = z3.number_input(L["ship_fee"], value=0.0)

                    st.divider()
                    if st.button(L["btn_out_confirm"], type="primary", use_container_width=True):
                        if not del_place or not del_phone or not zip_code or not del_addr:
                            st.error("납품처 회사명, 전화번호, 우편번호, 상세주소를 모두 입력해주세요.")
                        else:
                            run_commit("UPDATE inventory SET quantity=%s WHERE item_code=%s AND lot_no=%s AND warehouse=%s;", (sel_lot['quantity'] - out_qty, item_code, sel_lot['lot_no'], out_wh))
                            
                            run_commit("""INSERT INTO stock_movements (
                                            movement_date, movement_type, transaction_type, outbound_type, 
                                            item_code, item_name, lot_no, warehouse, quantity, 
                                            unit_price, total_amount, customer_name, po_number, 
                                            delivery_place, zip_code, delivery_address, delivery_phone, shipping_fee
                                          ) VALUES (%s, 'OUT', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                                       (out_date, out_trans, out_trans, item_code, item_name, sel_lot['lot_no'], out_wh, out_qty, price_jpy, total_amount, selected_cust, po_num, del_place, zip_code, del_addr, del_phone, ship_fee))
                            
                            st.success(f"✅ [{item_name}] {out_qty}개 출고 등록 및 재고 차감이 완료되었습니다!")
                            st.rerun()
                else:
                    st.warning("⚠️ 선택한 창고에 해당 상품의 출고 가능한 재고(LOT)가 없습니다.")

    # --- 📋 기간별 입출고 이력 ---
    elif selected_menu_key == "m_history":
        c1, c2 = st.columns(2)
        dates = c1.date_input("Period", [datetime.today() - timedelta(days=30), datetime.today()])
        m_type = c2.selectbox("Type", ["ALL", "IN (KRW ₩)", "OUT (JPY ￥)"])
        
        if len(dates) == 2:
            query = "SELECT movement_date, movement_type, transaction_type, warehouse, item_name, lot_no, quantity, unit_price, total_amount, customer_name, delivery_place, zip_code, delivery_address, delivery_phone FROM stock_movements WHERE movement_date BETWEEN %s AND %s"
            params = [dates[0], dates[1]]
            if m_type != "ALL":
                query += " AND movement_type = %s"
                params.append("IN" if "IN" in m_type else "OUT")
            
            df = run_query(query + " ORDER BY movement_date DESC;", params)
            if df:
                st.dataframe(pd.DataFrame(df), use_container_width=True)

    # --- 🏢 거래처 & 납품단가 관리 (엔화 ￥) ---
    elif selected_menu_key == "m_cust" and role != "guest":
        st.subheader(L["add_cust_title"])
        new_cust = st.text_input(L["new_cust_name"])
        if st.button(L["btn_add_cust"]) and new_cust: 
            run_commit("INSERT INTO customers (customer_name) VALUES (%s);", (new_cust,))
            st.success("Added.")
            st.rerun()
            
        st.divider()
        
        custs = [c['customer_name'] for c in fetch_customers()]
        if custs:
            sel_c = st.selectbox(L["sel_cust_mgt"], custs)
            
            st.markdown(f"#### {L['price_reg_title'].format(cust=sel_c)}")
            master_prods = fetch_master_products()
            
            col_a, col_b = st.columns(2)
            if master_prods:
                m_opts = {f"{m['item_name']} ({m['item_code']})": m for m in master_prods}
                sel_m = col_a.selectbox(L["sel_master"], list(m_opts.keys()))
                target_m = m_opts[sel_m]
                p_code = target_m['item_code']
                p_name = target_m['item_name']
            else:
                p_code = col_a.text_input(L["p_code"])
                p_name = col_a.text_input(L["p_name"])
                
            p_price = col_b.number_input(L["price_jpy"], value=0.0, key="new_p_price")
            
            if st.button(L["btn_add_price"], type="primary") and p_code and p_name:
                run_commit(
                    "INSERT INTO customer_prices (customer_name, item_code, item_name, delivery_price) VALUES (%s,%s,%s,%s) ON CONFLICT (customer_name, item_code) DO UPDATE SET delivery_price=EXCLUDED.delivery_price, item_name=EXCLUDED.item_name;",
                    (sel_c, p_code, p_name, p_price)
                )
                st.success("Saved.")
                st.rerun()

            st.divider()
            st.markdown(f"##### {L['price_list_title'].format(cust=sel_c)}")
            curr_prices = fetch_customer_prices(sel_c)
            
            if curr_prices:
                for cp in curr_prices:
                    row_id = cp['id']
                    c_code, c_name, c_price, c_save, c_del = st.columns([2.5, 3.5, 2, 1.2, 1.2])
                    
                    edit_code = c_code.text_input("Code", value=cp['item_code'], key=f"code_{row_id}", label_visibility="collapsed")
                    edit_name = c_name.text_input("Name", value=cp['item_name'], key=f"name_{row_id}", label_visibility="collapsed")
                    edit_price = c_price.number_input("Price", value=float(cp['delivery_price']), key=f"price_{row_id}", label_visibility="collapsed")
                    
                    if c_save.button(L["btn_edit_prod"], key=f"edit_{row_id}", use_container_width=True):
                        if edit_code and edit_name:
                            run_commit(
                                "UPDATE customer_prices SET item_code=%s, item_name=%s, delivery_price=%s WHERE id=%s;",
                                (edit_code, edit_name, edit_price, row_id)
                            )
                            st.success("Updated.")
                            st.rerun()
                            
                    if c_del.button(L["btn_del_prod"], key=f"del_{row_id}", type="secondary", use_container_width=True):
                        run_commit("DELETE FROM customer_prices WHERE id=%s;", (row_id,))
                        st.warning("Deleted.")
                        st.rerun()

    # --- 👥 계정 관리 ---
    elif selected_menu_key == "m_user" and role == "admin":
        st.subheader("👥 Account Management")
        pending_users = run_query("SELECT username, name, role FROM users WHERE status='pending';")
        if pending_users:
            for u in pending_users:
                col1, col2, col3 = st.columns([3, 2, 2])
                col1.write(f"**Username:** {u['username']} ({u.get('name', 'N/A')})")
                col2.write(f"**Role:** {u.get('role', 'staff')}")
                if col3.button("Approve", key=f"approve_{u['username']}"):
                    run_commit("UPDATE users SET status='active' WHERE username=%s;", (u['username'],))
                    st.success("Approved.")
                    st.rerun()
        else:
            st.info("No pending users.")
