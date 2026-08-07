import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

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
    if conn is None:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                return results
            return []
    except Exception as e:
        st.error(f"쿼리 실행 오류: {e}")
        return []
    finally:
        conn.close()

def run_commit(query, params=None):
    conn = get_connection()
    if conn is None:
        return False
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
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = "guest"

# --- 4. 로그인 및 회원가입 화면 ---
if not st.session_state["logged_in"]:
    st.title("✨ GPCLUB JAPAN ERP")
    tab1, tab2 = st.tabs(["🔒 로그인", "📝 회원가입 신청"])
    
    with tab1:
        username_input = st.text_input("아이디")
        password_input = st.text_input("비밀번호", type="password")
        
        if st.button("로그인", use_container_width=True):
            user = run_query(
                "SELECT * FROM users WHERE username=%s AND password=%s AND status='active';",
                (username_input, password_input)
            )
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = user[0]['username']
                st.session_state["role"] = user[0].get('role', 'staff')
                role_korean = {"admin": "관리자", "staff": "사원", "guest": "방문자"}.get(st.session_state["role"], "방문자")
                st.success(f"환영합니다, {user[0]['username']}님! [{role_korean}] 권한으로 로그인되었습니다.")
                st.rerun()
            else:
                st.error("아이디/비밀번호가 올바르지 않거나 승인 대기 중인 계정입니다.")

    with tab2:
        st.subheader("신규 계정 가입 신청")
        new_user = st.text_input("신청 아이디")
        new_pass = st.text_input("신청 비밀번호", type="password")
        new_name = st.text_input("이름")
        role_map = {"사원": "staff", "관리자": "admin", "방문자": "guest"}
        selected_role_label = st.selectbox("요청 권한", ["사원", "관리자", "방문자"])
        req_role = role_map[selected_role_label]
        
        if st.button("가입 신청 제출", use_container_width=True):
            if new_user and new_pass:
                existing = run_query("SELECT * FROM users WHERE username=%s;", (new_user,))
                if existing:
                    st.warning("이미 존재하는 아이디입니다.")
                else:
                    success = run_commit(
                        "INSERT INTO users (username, password, name, role, status) VALUES (%s, %s, %s, %s, 'pending');",
                        (new_user, new_pass, new_name, req_role)
                    )
                    if success:
                        st.success("가입 신청이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.")
            else:
                st.warning("아이디와 비밀번호를 입력해주세요.")

# --- 5. 메인 ERP 화면 (로그인 성공 시) ---
else:
    role = st.session_state["role"]
    role_korean = {"admin": "관리자", "staff": "사원", "guest": "방문자"}.get(role, "방문자")
    warehouses = ["SAGAWA", "L&K", "大吉商事"]
    
    # 사이드바 Navigation
    st.sidebar.title("✨ GPCLUB JAPAN")
    st.sidebar.write(f"접속자: **{st.session_state['username']}** ({role_korean})")
    
    menu_options = ["📊 대시보드 & 잔여재고", "📥 입고 등록", "📤 출고 등록", "🏢 거래처 & 단가 관리"]
    if role == "admin":
        menu_options.append("👥 계정 승인 및 관리")
        
    menu = st.sidebar.radio("메뉴 선택", menu_options)
    
    if st.sidebar.button("로그아웃"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = "guest"
        st.rerun()

    st.title(f"✨ GPCLUB JAPAN ERP - {menu}")

    # --------------------------------------------------
    # 1) 대시보드 & 잔여재고
    # --------------------------------------------------
    if menu == "📊 대시보드 & 잔여재고":
        current_month = datetime.now().strftime('%Y-%m')
        wh_filter = st.selectbox("🏬 창고 선택 필터", ["전체 (통합 대시보드)"] + warehouses)

        if wh_filter == "전체 (통합 대시보드)":
            st.subheader("🌐 전체 창고 통합 요약")
            
            # KPI 지표 계산
            total_stock_qty = run_query("SELECT SUM(quantity) as val FROM inventory;")[0]['val'] or 0
            total_stock_val = run_query("SELECT SUM(quantity * purchase_price) as val FROM inventory;")[0]['val'] or 0
            month_in_qty = run_query(
                "SELECT SUM(quantity) as val FROM stock_movements WHERE movement_type='IN' AND TO_CHAR(created_at, 'YYYY-MM')=%s;",
                (current_month,)
            )[0]['val'] or 0
            month_out_qty = run_query(
                "SELECT SUM(quantity) as val FROM stock_movements WHERE movement_type='OUT' AND TO_CHAR(created_at, 'YYYY-MM')=%s;",
                (current_month,)
            )[0]['val'] or 0

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("📦 총 재고 수량", f"{total_stock_qty:,} 개")
            kpi2.metric("💰 총 재고 금액 (매입가)", f"￥{total_stock_val:,.0f}")
            kpi3.metric("📥 이번달 총 입고량", f"{month_in_qty:,} 개")
            kpi4.metric("📤 이번달 총 출고량", f"{month_out_qty:,} 개")

            st.divider()
            st.subheader("📋 상품명별 통합 묶음 재고 현황")
            grouped_data = run_query("""
                SELECT item_name, jan_code, SUM(quantity) as total_qty, 
                       ROUND(AVG(purchase_price), 2) as avg_purchase_price,
                       SUM(quantity * purchase_price) as total_val
                FROM inventory
                GROUP BY item_name, jan_code
                ORDER BY item_name;
            """)
            if grouped_data:
                df_grouped = pd.DataFrame(grouped_data)
                df_grouped.columns = ["제품명", "JAN 코드", "총 재고수량", "평균 매입단가(￥)", "총 재고금액(￥)"]
                st.dataframe(df_grouped, use_container_width=True)
            else:
                st.info("등록된 재고 데이터가 없습니다.")

        else: # 개별 창고 선택 시
            st.subheader(f"🏬 [{wh_filter}] 창고 현황")
            wh_stock_qty = run_query("SELECT SUM(quantity) as val FROM inventory WHERE warehouse=%s;", (wh_filter,))[0]['val'] or 0
            wh_stock_val = run_query("SELECT SUM(quantity * purchase_price) as val FROM inventory WHERE warehouse=%s;", (wh_filter,))[0]['val'] or 0
            wh_month_in = run_query(
                "SELECT SUM(quantity) as val FROM stock_movements WHERE movement_type='IN' AND warehouse=%s AND TO_CHAR(created_at, 'YYYY-MM')=%s;",
                (wh_filter, current_month)
            )[0]['val'] or 0
            wh_month_out = run_query(
                "SELECT SUM(quantity) as val FROM stock_movements WHERE movement_type='OUT' AND warehouse=%s AND TO_CHAR(created_at, 'YYYY-MM')=%s;",
                (wh_filter, current_month)
            )[0]['val'] or 0

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("창고 잔여재고", f"{wh_stock_qty:,} 개")
            k2.metric("창고 재고금액(매입가)", f"￥{wh_stock_val:,.0f}")
            k3.metric("월간 입고량", f"{wh_month_in:,} 개")
            k4.metric("월간 출고량", f"{wh_month_out:,} 개")

            st.divider()
            st.subheader(f"🔍 [{wh_filter}] 상세 세부 재고 (LOT별)")
            detail_data = run_query("""
                SELECT item_code, item_name, jan_code, lot_no, quantity, purchase_price, (quantity * purchase_price) as total_amount
                FROM inventory WHERE warehouse=%s ORDER BY item_code, lot_no;
            """, (wh_filter,))
            if detail_data:
                df_detail = pd.DataFrame(detail_data)
                df_detail.columns = ["제품코드", "제품명", "JAN코드", "LOT번호", "수량", "매입단가(￥)", "총 재고금액(￥)"]
                st.dataframe(df_detail, use_container_width=True)
            else:
                st.info(f"{wh_filter} 창고에 재고가 없습니다.")

    # --------------------------------------------------
    # 2) 입고 등록 (사원, 관리자만)
    # --------------------------------------------------
    elif menu == "📥 입고 등록":
        if role == "guest":
            st.warning("🔒 방문자는 조회만 가능합니다.")
        else:
            st.subheader("📥 제품 입고 입력 (재고 증가)")
            c1, c2, c3 = st.columns(3)
            with c1:
                in_code = st.text_input("제품코드*")
                in_name = st.text_input("제품명*")
                in_jan = st.text_input("JAN 코드")
            with c2:
                in_lot = st.text_input("LOT 번호*")
                in_wh = st.selectbox("입고 창고명*", warehouses)
            with c3:
                in_qty = st.number_input("입고 수량*", min_value=1, value=1)
                in_price = st.number_input("매입 단가(￥)*", min_value=0.0, value=0.0, step=100.0)

            calc_total = in_qty * in_price
            st.info(f"💡 **총 입고 예상 금액:** ￥{calc_total:,.0f}")

            if st.button("입고 확정 및 저장", use_container_width=True):
                if in_code and in_name and in_lot and in_wh and in_qty > 0:
                    # Inventory Upsert
                    ex = run_query("SELECT id, quantity FROM inventory WHERE item_code=%s AND lot_no=%s AND warehouse=%s;", (in_code, in_lot, in_wh))
                    if ex:
                        new_q = ex[0]['quantity'] + in_qty
                        run_commit("UPDATE inventory SET quantity=%s, purchase_price=%s, item_name=%s, jan_code=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s;",
                                   (new_q, in_price, in_name, in_jan, ex[0]['id']))
                    else:
                        run_commit("INSERT INTO inventory (item_code, item_name, jan_code, lot_no, warehouse, quantity, purchase_price) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                                   (in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price))
                    
                    # Stock Movement 이력 등록
                    run_commit("""
                        INSERT INTO stock_movements (movement_type, item_code, item_name, jan_code, lot_no, warehouse, quantity, unit_price, total_amount)
                        VALUES ('IN', %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price, calc_total))

                    st.success("입고가 성공적으로 등록되었습니다.")
                    st.rerun()
                else:
                    st.warning("필수 입력란(*)을 모두 작성해 주세요.")

    # --------------------------------------------------
    # 3) 출고 등록 (거래처 단가 자동 매핑)
    # --------------------------------------------------
    elif menu == "📤 출고 등록":
        if role == "guest":
            st.warning("🔒 방문자는 조회만 가능합니다.")
        else:
            st.subheader("📤 제품 출고 입력 (거래처 단가자동 매핑 및 재고 차감)")
            
            cust_list = [c['customer_name'] for c in run_query("SELECT customer_name FROM customers ORDER BY customer_name;")]
            if not cust_list:
                st.warning("⚠️ 등록된 거래처가 없습니다. 먼저 [🏢 거래처 & 단가 관리] 메뉴에서 거래처와 품목 단가를 등록하세요.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    selected_cust = st.selectbox("거래처 선택*", cust_list)
                    
                    # 해당 거래처에 등록된 단가 품목 가져오기
                    cust_items = run_query("SELECT item_code, item_name, jan_code, delivery_price FROM customer_prices WHERE customer_name=%s;", (selected_cust,))
                    item_options = {f"{i['item_name']} ({i['item_code']}) - 납품가: ￥{i['delivery_price']:,}": i for i in cust_items}
                    
                    if not item_options:
                        st.error("해당 거래처에 등록된 품목 단가가 없습니다. 단가 관리를 완료해 주세요.")
                        selected_item = None
                    else:
                        selected_item_label = st.selectbox("출고 품목 선택*", list(item_options.keys()))
                        selected_item = item_options[selected_item_label]

                with c2:
                    out_wh = st.selectbox("출고 창고명*", warehouses)
                    
                    # 선택된 품목 & 창고의 잔여 재고 및 LOT 가져오기
                    if selected_item:
                        available_lots = run_query(
                            "SELECT lot_no, quantity FROM inventory WHERE item_code=%s AND warehouse=%s AND quantity > 0;",
                            (selected_item['item_code'], out_wh)
                        )
                        lot_options = {f"LOT: {l['lot_no']} (현재 재고: {l['quantity']}개)": l for l in available_lots}
                        
                        if not lot_options:
                            st.warning(f"선택한 창고 [{out_wh}]에 해당 품목의 잔여 재고가 없습니다.")
                            selected_lot = None
                        else:
                            selected_lot_label = st.selectbox("출고할 LOT 선택*", list(lot_options.keys()))
                            selected_lot = lot_options[selected_lot_label]
                    else:
                        selected_lot = None

                st.divider()
                if selected_item and selected_lot:
                    col_q, col_p = st.columns(2)
                    with col_q:
                        out_qty = st.number_input("출고 수량*", min_value=1, max_value=selected_lot['quantity'], value=1)
                    with col_p:
                        auto_price = selected_item['delivery_price']
                        st.text_input("거래처 자동 매핑 납품 단가(￥)", value=f"￥{auto_price:,.0f}", disabled=True)
                    
                    out_total = out_qty * auto_price
                    st.info(f"💡 **총 출고 금액:** ￥{out_total:,.0f}")

                    if st.button("출고 확정 및 차감", use_container_width=True):
                        # 재고 차감
                        new_inv_qty = selected_lot['quantity'] - out_qty
                        run_commit("UPDATE inventory SET quantity=%s, updated_at=CURRENT_TIMESTAMP WHERE item_code=%s AND lot_no=%s AND warehouse=%s;",
                                   (new_inv_qty, selected_item['item_code'], selected_lot['lot_no'], out_wh))
                        
                        # Stock Movement 출고 이력
                        run_commit("""
                            INSERT INTO stock_movements (movement_type, item_code, item_name, jan_code, lot_no, warehouse, quantity, unit_price, total_amount, customer_name)
                            VALUES ('OUT', %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (selected_item['item_code'], selected_item['item_name'], selected_item['jan_code'], selected_lot['lot_no'], out_wh, out_qty, auto_price, out_total, selected_cust))

                        st.success("출고 처리가 정상 등록되고 재고가 차감되었습니다.")
                        st.rerun()

    # --------------------------------------------------
    # 4) 거래처 & 단가 관리
    # --------------------------------------------------
    elif menu == "🏢 거래처 & 단가 관리":
        if role == "guest":
            st.warning("🔒 방문자는 등록/수정이 불가합니다.")
        else:
            t1, t2 = st.tabs(["🏢 거래처 등록", "🏷️ 거래처별 납품 단가 관리"])
            
            with t1:
                st.subheader("신규 거래처 등록")
                new_cust = st.text_input("거래처명 입력")
                if st.button("거래처 추가"):
                    if new_cust:
                        if run_commit("INSERT INTO customers (customer_name) VALUES (%s);", (new_cust,)):
                            st.success(f"거래처 [{new_cust}]가 등록되었습니다.")
                            st.rerun()
                    else:
                        st.warning("거래처명을 입력하세요.")
                
                st.divider()
                st.write("📋 현재 등록된 거래처 목록")
                c_data = run_query("SELECT id, customer_name, created_at FROM customers ORDER BY id DESC;")
                if c_data:
                    st.dataframe(pd.DataFrame(c_data), use_container_width=True)

            with t2:
                st.subheader("거래처별 지정 품목 납품 단가 설정")
                cust_list = [c['customer_name'] for c in run_query("SELECT customer_name FROM customers ORDER BY customer_name;")]
                if not cust_list:
                    st.info("먼저 거래처를 등록해주세요.")
                else:
                    sel_c = st.selectbox("거래처 선택", cust_list, key="price_cust_sel")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        p_code = st.text_input("품목 코드*")
                        p_name = st.text_input("품목명*")
                    with c2:
                        p_jan = st.text_input("JAN 코드")
                        p_del_price = st.number_input("지정 납품 단가(￥)*", min_value=0.0, value=0.0, step=100.0)
                    
                    if st.button("거래처 단가 저장/수정"):
                        if p_code and p_name:
                            run_commit("""
                                INSERT INTO customer_prices (customer_name, item_code, item_name, jan_code, delivery_price)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT (customer_name, item_code) 
                                DO UPDATE SET delivery_price=EXCLUDED.delivery_price, item_name=EXCLUDED.item_name, jan_code=EXCLUDED.jan_code;
                            """, (sel_c, p_code, p_name, p_jan, p_del_price))
                            st.success(f"[{sel_c}] 의 [{p_name}] 납품 단가(￥{p_del_price:,.0f})가 저장되었습니다.")
                            st.rerun()
                        else:
                            st.warning("품목코드와 품목명을 입력하세요.")

                    st.divider()
                    st.write(f"📋 [{sel_c}] 등록 단가 리스트")
                    cp_data = run_query("SELECT item_code, item_name, jan_code, delivery_price FROM customer_prices WHERE customer_name=%s;", (sel_c,))
                    if cp_data:
                        df_cp = pd.DataFrame(cp_data)
                        df_cp.columns = ["품목코드", "품목명", "JAN코드", "납품단가(￥)"]
                        st.dataframe(df_cp, use_container_width=True)

    # --------------------------------------------------
    # 5) 계정 승인 및 관리 (관리자)
    # --------------------------------------------------
    elif menu == "👥 계정 승인 및 관리" and role == "admin":
        st.header("👥 계정 승인 및 권한 관리 시스템")
        
        st.subheader("⏳ 승인 대기 신청 (Pending)")
        pending_users = run_query("SELECT id, username, name, role FROM users WHERE status='pending';")
        
        if pending_users:
            role_labels = {"admin": "관리자", "staff": "사원", "guest": "방문자"}
            for u in pending_users:
                col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1])
                col1.write(f"**{u['username']}** ({u['name']})")
                col2.write(f"요청권한: **{role_labels.get(u['role'], u['role'])}**")
                
                if col3.button("승인", key=f"app_{u['id']}"):
                    run_commit("UPDATE users SET status='active' WHERE id=%s;", (u['id'],))
                    st.success(f"{u['username']} 계정을 승인했습니다.")
                    st.rerun()
                if col4.button("거절", key=f"rej_{u['id']}"):
                    run_commit("UPDATE users SET status='rejected' WHERE id=%s;", (u['id'],))
                    st.warning(f"{u['username']} 계정을 거절했습니다.")
                    st.rerun()
        else:
            st.info("대기 중인 가입 신청이 없습니다.")
            
        st.divider()
        st.subheader("⚙️ 전체 계정 목록 및 권한 수정")
        all_users = run_query("SELECT id, username, name, role, status FROM users WHERE username != 'admin';")
        
        if all_users:
            role_options = ["사원", "관리자", "방문자"]
            role_to_code = {"사원": "staff", "관리자": "admin", "방문자": "guest"}
            code_to_role = {"staff": "사원", "admin": "관리자", "guest": "방문자"}
            
            for u in all_users:
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 1, 1])
                status_icon = "🟢 활성" if u['status'] == 'active' else "🔴 비활성"
                
                col1.write(f"**{u['username']}** ({u['name']}) [{status_icon}]")
                current_role_label = code_to_role.get(u['role'], "방문자")
                new_role_label = col2.selectbox("권한 변경", role_options, index=role_options.index(current_role_label), key=f"role_sel_{u['id']}")
                
                if col3.button("권한 저장", key=f"save_role_{u['id']}"):
                    new_code = role_to_code[new_role_label]
                    run_commit("UPDATE users SET role=%s WHERE id=%s;", (new_code, u['id']))
                    st.success(f"{u['username']} 님의 권한이 [{new_role_label}]로 변경되었습니다.")
                    st.rerun()
                
                if u['status'] == 'active':
                    if col4.button("비활성화", key=f"deact_{u['id']}"):
                        run_commit("UPDATE users SET status='disabled' WHERE id=%s;", (u['id'],))
                        st.rerun()
                else:
                    if col4.button("활성화", key=f"act_{u['id']}"):
                        run_commit("UPDATE users SET status='active' WHERE id=%s;", (u['id'],))
                        st.rerun()
                        
                if col5.button("삭제", key=f"del_{u['id']}"):
                    run_commit("DELETE FROM users WHERE id=%s;", (u['id'],))
                    st.success("계정이 삭제되었습니다.")
                    st.rerun()
        else:
            st.write("등록된 일반 계정이 없습니다.")
