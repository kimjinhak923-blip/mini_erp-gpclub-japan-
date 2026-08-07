import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 페이지 기본 설정 ---
st.set_page_config(
    page_title="GPCLUB JAPAN ERP",
    page_icon="✨",
    layout="wide"
)

# --- 2. DB 연결 및 실행 함수 ---
def get_connection():
    try:
        return psycopg2.connect(
            host=st.secrets.get("DB_HOST"),
            database=st.secrets.get("DB_NAME", "postgres"),
            user=st.secrets.get("DB_USER"),
            password=st.secrets.get("DB_PASSWORD"),
            port=st.secrets.get("DB_PORT", "6543")
        )
    except Exception as e:
        st.error(f"DB 연결 오류: {e}\nStreamlit Secrets 설정을 확인하세요.")
        return None

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
        st.error(f"쿼리 실행 오류: {e}")
        return []
    finally:
        conn.close()

def run_commit(query, params=None):
    conn = get_connection()
    if conn is None: return False
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"데이터 저장 오류: {e}")
        return False
    finally:
        conn.close()

# --- 3. 세션 상태 초기화 ---
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": "", "role": "guest"})

# --- 4. 로그인 및 회원가입 화면 ---
if not st.session_state["logged_in"]:
    st.title("✨ GPCLUB JAPAN ERP")
    tab1, tab2 = st.tabs(["🔒 로그인", "📝 회원가입 신청"])
    
    with tab1:
        username_input = st.text_input("아이디")
        password_input = st.text_input("비밀번호", type="password")
        if st.button("로그인", use_container_width=True):
            user = run_query("SELECT * FROM users WHERE username=%s AND password=%s AND status='active';", (username_input, password_input))
            if user:
                st.session_state.update({"logged_in": True, "username": user[0]['username'], "role": user[0].get('role', 'staff')})
                st.rerun()
            else:
                st.error("아이디/비밀번호가 올바르지 않거나 승인 대기 중인 계정입니다.")

    with tab2:
        new_user = st.text_input("신청 아이디")
        new_pass = st.text_input("신청 비밀번호", type="password")
        new_name = st.text_input("이름")
        req_role = {"사원": "staff", "관리자": "admin", "방문자": "guest"}[st.selectbox("요청 권한", ["사원", "관리자", "방문자"])]
        if st.button("가입 신청 제출"):
            if new_user and new_pass:
                if run_query("SELECT * FROM users WHERE username=%s;", (new_user,)):
                    st.warning("이미 존재하는 아이디입니다.")
                elif run_commit("INSERT INTO users (username, password, name, role, status) VALUES (%s, %s, %s, %s, 'pending');", (new_user, new_pass, new_name, req_role)):
                    st.success("가입 신청 완료.")
            else:
                st.warning("아이디/비밀번호를 입력하세요.")

# --- 5. 메인 ERP 화면 ---
else:
    role = st.session_state["role"]
    warehouses = ["SAGAWA", "L&K", "大吉商事"]
    
    st.sidebar.title("✨ GPCLUB JAPAN")
    menu_options = ["📊 대시보드 & 잔여재고", "📥 입고 등록", "📤 출고 등록", "📋 기간별 입출고 이력", "🏢 거래처 & 단가 관리"]
    if role == "admin": menu_options.append("👥 계정 관리")
    menu = st.sidebar.radio("메뉴 선택", menu_options)
    
    if st.sidebar.button("로그아웃"):
        st.session_state.update({"logged_in": False, "username": "", "role": "guest"})
        st.rerun()

    st.title(f"✨ GPCLUB JAPAN ERP - {menu}")

    # --- 1) 대시보드 ---
    if menu == "📊 대시보드 & 잔여재고":
        current_month = datetime.now().strftime('%Y-%m')
        wh_filter = st.selectbox("🏬 창고 필터", ["전체"] + warehouses)

        if wh_filter == "전체":
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("총 재고 수량", f"{run_query('SELECT SUM(quantity) as v FROM inventory;')[0]['v'] or 0:,} 개")
            k2.metric("총 재고 금액(￥)", f"￥{run_query('SELECT SUM(quantity * purchase_price) as v FROM inventory;')[0]['v'] or 0:,.0f}")
            k3.metric("이번달 총 입고", f"{run_query('SELECT SUM(quantity) as v FROM stock_movements WHERE movement_type=''IN'' AND TO_CHAR(movement_date, ''YYYY-MM'')=%s;', (current_month,))[0]['v'] or 0:,} 개")
            k4.metric("이번달 총 출고", f"{run_query('SELECT SUM(quantity) as v FROM stock_movements WHERE movement_type=''OUT'' AND TO_CHAR(movement_date, ''YYYY-MM'')=%s;', (current_month,))[0]['v'] or 0:,} 개")

            st.subheader("📋 제품 통합 재고")
            df = run_query("SELECT item_name, jan_code, SUM(quantity) as qty, AVG(purchase_price) as avg_p, SUM(quantity * purchase_price) as tot FROM inventory GROUP BY item_name, jan_code ORDER BY item_name;")
            if df: st.dataframe(pd.DataFrame(df).rename(columns={"item_name":"제품명", "jan_code":"JAN", "qty":"총수량", "avg_p":"평균매입가", "tot":"총금액"}), use_container_width=True)
        else:
            st.subheader(f"🏬 {wh_filter} 창고 상세 (LOT별)")
            df = run_query("SELECT item_code, item_name, lot_no, quantity, purchase_price, (quantity*purchase_price) as tot FROM inventory WHERE warehouse=%s;", (wh_filter,))
            if df: st.dataframe(pd.DataFrame(df).rename(columns={"item_code":"코드", "item_name":"제품명", "lot_no":"LOT", "quantity":"수량", "purchase_price":"매입단가", "tot":"총금액"}), use_container_width=True)

    # --- 2) 입고 등록 ---
    elif menu == "📥 입고 등록" and role != "guest":
        col1, col2, col3 = st.columns(3)
        with col1:
            in_date = st.date_input("입고 일자*", datetime.today())
            in_type = st.selectbox("매입/제공 유형*", ["매입/발주납품", "FOC무료제공"])
            in_code = st.text_input("제품코드*")
        with col2:
            in_name = st.text_input("제품명*")
            in_jan = st.text_input("JAN 코드")
            in_lot = st.text_input("LOT 번호*")
        with col3:
            in_wh = st.selectbox("입고 창고*", warehouses)
            in_qty = st.number_input("입고 수량*", min_value=1)
            in_price = st.number_input("매입 단가(￥)*", value=0.0 if in_type == "FOC무료제공" else 0.0)

        if st.button("입고 확정"):
            if in_code and in_name and in_lot:
                ex = run_query("SELECT id, quantity FROM inventory WHERE item_code=%s AND lot_no=%s AND warehouse=%s;", (in_code, in_lot, in_wh))
                if ex: run_commit("UPDATE inventory SET quantity=%s, purchase_price=%s WHERE id=%s;", (ex[0]['quantity']+in_qty, in_price, ex[0]['id']))
                else: run_commit("INSERT INTO inventory (item_code, item_name, jan_code, lot_no, warehouse, quantity, purchase_price) VALUES (%s, %s, %s, %s, %s, %s, %s);", (in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price))
                
                run_commit("INSERT INTO stock_movements (movement_date, movement_type, transaction_type, item_code, item_name, jan_code, lot_no, warehouse, quantity, unit_price, total_amount) VALUES (%s, 'IN', %s, %s, %s, %s, %s, %s, %s, %s, %s);", 
                           (in_date, in_type, in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price, in_qty*in_price))
                st.success("입고 완료")
                st.rerun()

    # --- 3) 출고 등록 ---
    elif menu == "📤 출고 등록" and role != "guest":
        c1, c2, c3, c4 = st.columns(4)
        out_date = c1.date_input("출고 일자*", datetime.today())
        out_trans = c2.selectbox("매입/제공 유형*", ["발주납품", "FOC무료제공"])
        out_type = c3.selectbox("출고 세부 유형*", ["발주", "샘플발송"])
        out_wh = c4.selectbox("출고 창고*", warehouses)

        cust_list = [c['customer_name'] for c in run_query("SELECT customer_name FROM customers;")]
        selected_cust = st.selectbox("발주 거래처*", cust_list) if cust_list else None
        
        if selected_cust:
            items = {f"{i['item_name']} (￥{i['delivery_price']})": i for i in run_query("SELECT * FROM customer_prices WHERE customer_name=%s;", (selected_cust,))}
            sel_item = items.get(st.selectbox("품목*", list(items.keys()))) if items else None
            
            if sel_item:
                lots = {f"LOT: {l['lot_no']} (재고:{l['quantity']})": l for l in run_query("SELECT * FROM inventory WHERE item_code=%s AND warehouse=%s AND quantity>0;", (sel_item['item_code'], out_wh))}
                sel_lot = lots.get(st.selectbox("LOT*", list(lots.keys()))) if lots else None
                
                if sel_lot:
                    out_qty = st.number_input("수량*", min_value=1, max_value=sel_lot['quantity'])
                    price = 0 if out_trans == "FOC무료제공" else sel_item['delivery_price']
                    
                    st.divider()
                    st.markdown("##### 🚚 배송 및 추가 정보")
                    d1, d2, d3 = st.columns(3)
                    po_num = d1.text_input("발주 번호")
                    del_place = d2.text_input("납품처명")
                    del_phone = d3.text_input("전화번호")
                    
                    z1, z2 = st.columns([1,3])
                    zip_code = z1.text_input("우편번호")
                    del_addr = z2.text_input("상세 주소")
                    ship_fee = st.number_input("배송비(￥)", value=0.0)

                    if st.button("출고 확정 및 재고 차감", type="primary"):
                        run_commit("UPDATE inventory SET quantity=%s WHERE item_code=%s AND lot_no=%s AND warehouse=%s;", (sel_lot['quantity']-out_qty, sel_item['item_code'], sel_lot['lot_no'], out_wh))
                        run_commit("""INSERT INTO stock_movements (movement_date, movement_type, transaction_type, outbound_type, item_code, item_name, lot_no, warehouse, quantity, unit_price, total_amount, customer_name, po_number, delivery_place, zip_code, delivery_address, delivery_phone, shipping_fee) 
                                      VALUES (%s, 'OUT', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                                   (out_date, out_trans, out_type, sel_item['item_code'], sel_item['item_name'], sel_lot['lot_no'], out_wh, out_qty, price, out_qty*price, selected_cust, po_num, del_place, zip_code, del_addr, del_phone, ship_fee))
                        st.success("출고 완료")
                        st.rerun()

    # --- 4) 기간별 입출고 이력 ---
    elif menu == "📋 기간별 입출고 이력":
        c1, c2 = st.columns(2)
        dates = c1.date_input("조회 기간 (시작일 - 종료일)", [datetime.today() - timedelta(days=30), datetime.today()])
        m_type = c2.selectbox("입출고 구분", ["전체", "입고 (IN)", "출고 (OUT)"])
        
        if len(dates) == 2:
            query = "SELECT movement_date as 일자, movement_type as 구분, transaction_type as 유형, outbound_type as 출고구분, warehouse as 창고, item_name as 제품명, lot_no as LOT, quantity as 수량, total_amount as 금액, customer_name as 거래처, shipping_fee as 배송비, zip_code as 우편번호, delivery_place as 납품처 FROM stock_movements WHERE movement_date BETWEEN %s AND %s"
            params = [dates[0], dates[1]]
            if m_type != "전체":
                query += " AND movement_type = %s"
                params.append("IN" if "입고" in m_type else "OUT")
            
            df = run_query(query + " ORDER BY movement_date DESC;", params)
            if df: st.dataframe(pd.DataFrame(df), use_container_width=True)
            else: st.info("조건에 맞는 이력이 없습니다.")

    # --- 5) 거래처 & 단가 관리 ---
    elif menu == "🏢 거래처 & 단가 관리" and role != "guest":
        new_cust = st.text_input("새 거래처명")
        if st.button("추가") and new_cust: run_commit("INSERT INTO customers (customer_name) VALUES (%s);", (new_cust,))
        st.divider()
        
        custs = [c['customer_name'] for c in run_query("SELECT customer_name FROM customers;")]
        if custs:
            sel_c = st.selectbox("거래처 선택", custs)
            p_code = st.text_input("품목코드")
            p_name = st.text_input("품목명")
            p_price = st.number_input("납품단가(￥)")
            if st.button("단가 저장") and p_code and p_name:
                run_commit("INSERT INTO customer_prices (customer_name, item_code, item_name, delivery_price) VALUES (%s,%s,%s,%s) ON CONFLICT (customer_name, item_code) DO UPDATE SET delivery_price=EXCLUDED.delivery_price, item_name=EXCLUDED.item_name;", (sel_c, p_code, p_name, p_price))
            
            df = run_query("SELECT item_code, item_name, delivery_price FROM customer_prices WHERE customer_name=%s;", (sel_c,))
            if df: st.dataframe(pd.DataFrame(df), use_container_width=True)

    # --- 6) 계정 관리 ---
    elif menu == "👥 계정 관리" and role == "admin":
        st.write("승인 대기")
        for u in run_query("SELECT * FROM users WHERE status='pending';"):
            if st.button(f"승인: {u['username']}", key=u['id']): run_commit("UPDATE users SET status='active' WHERE id=%s;", (u['id'],)); st.rerun()
