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
    menu_options = ["📊 대시보드 & 잔여재고", "📦 취급 제품 마스터", "📥 입고 등록", "📤 출고 등록", "📋 기간별 입출고 이력", "🏢 거래처 & 단가 관리"]
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
            total_qty = run_query("SELECT SUM(quantity) as v FROM inventory;")[0]['v'] or 0
            total_amt = run_query("SELECT SUM(quantity * purchase_price) as v FROM inventory;")[0]['v'] or 0
            month_in = run_query("SELECT SUM(quantity) as v FROM stock_movements WHERE movement_type=%s AND TO_CHAR(movement_date, 'YYYY-MM')=%s;", ('IN', current_month))[0]['v'] or 0
            month_out = run_query("SELECT SUM(quantity) as v FROM stock_movements WHERE movement_type=%s AND TO_CHAR(movement_date, 'YYYY-MM')=%s;", ('OUT', current_month))[0]['v'] or 0

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("총 재고 수량", f"{total_qty:,} 개")
            k2.metric("총 재고 금액(￥)", f"￥{total_amt:,.0f}")
            k3.metric("이번달 총 입고", f"{month_in:,} 개")
            k4.metric("이번달 총 출고", f"{month_out:,} 개")

            st.subheader("📋 제품 통합 재고")
            df = run_query("SELECT item_name, jan_code, SUM(quantity) as qty, AVG(purchase_price) as avg_p, SUM(quantity * purchase_price) as tot FROM inventory GROUP BY item_name, jan_code ORDER BY item_name;")
            if df: st.dataframe(pd.DataFrame(df).rename(columns={"item_name":"제품명", "jan_code":"JAN", "qty":"총수량", "avg_p":"평균매입가", "tot":"총금액"}), use_container_width=True)
        else:
            st.subheader(f"🏬 {wh_filter} 창고 상세 (LOT별)")
            df = run_query("SELECT item_code, item_name, lot_no, quantity, purchase_price, (quantity*purchase_price) as tot FROM inventory WHERE warehouse=%s;", (wh_filter,))
            if df: st.dataframe(pd.DataFrame(df).rename(columns={"item_code":"코드", "item_name":"제품명", "lot_no":"LOT", "quantity":"수량", "purchase_price":"매입단가", "tot":"총금액"}), use_container_width=True)

    # --- 2) 취급 제품 마스터 관리 ---
    elif menu == "📦 취급 제품 마스터" and role != "guest":
        # DB 컬럼 자동 확장 (기존 DB 컬럼 미존재 시 자동 생성)
        alter_cols = [
            "jan_box VARCHAR(100)", "jan_piece VARCHAR(100)",
            "box_in_box INT DEFAULT 0", "box_in_piece INT DEFAULT 0",
            "prod_size_w NUMERIC DEFAULT 0", "prod_size_d NUMERIC DEFAULT 0", "prod_size_h NUMERIC DEFAULT 0",
            "carton_size_w NUMERIC DEFAULT 0", "carton_size_d NUMERIC DEFAULT 0", "carton_size_h NUMERIC DEFAULT 0",
            "pallet_in_box INT DEFAULT 0", "pallet_in_carton INT DEFAULT 0"
        ]
        for col_def in alter_cols:
            run_commit(f"ALTER TABLE master_products ADD COLUMN IF NOT EXISTS {col_def};")

        tab_reg, tab_edit = st.tabs(["➕ 신규 제품 등록", "✏️ 기존 제품 수정 / 삭제"])

        # --- Tab 1: 신규 등록 ---
        with tab_reg:
            st.subheader("➕ 취급 제품 마스터 상세 등록")
            with st.form("master_product_form", clear_on_submit=False):
                st.markdown("##### 📌 기본 정보")
                c1, c2, c3 = st.columns(3)
                m_code = c1.text_input("제품 코드* (예: PROD-001)")
                m_name = c2.text_input("제품명*")
                m_price = c3.number_input("기본 매입단가(￥)", value=0.0, step=10.0)

                st.markdown("##### 🏷️ JAN 코드")
                j1, j2 = st.columns(2)
                m_jan_box = j1.text_input("JAN 코드 (곽/소박스)")
                m_jan_piece = j2.text_input("JAN 코드 (낱장/단품)")

                st.markdown("##### 📦 박스 입수량")
                b1, b2 = st.columns(2)
                m_box_in_box = b1.number_input("박스 당 곽 수량(개)", min_value=0, value=0)
                m_box_in_piece = b2.number_input("박스 당 낱장 수량(개)", min_value=0, value=0)

                st.markdown("##### 📐 곽(제품) 사이즈 (가로 x 세로 x 높이 mm)")
                ps1, ps2, ps3 = st.columns(3)
                m_ps_w = ps1.number_input("곽 가로(W)", min_value=0.0, value=0.0, step=1.0)
                m_ps_d = ps2.number_input("곽 세로(D)", min_value=0.0, value=0.0, step=1.0)
                m_ps_h = ps3.number_input("곽 높이(H)", min_value=0.0, value=0.0, step=1.0)

                st.markdown("##### 📦 박스 사이즈 (가로 x 세로 x 높이 mm)")
                cs1, cs2, cs3 = st.columns(3)
                m_cs_w = cs1.number_input("박스 가로(W)", min_value=0.0, value=0.0, step=1.0)
                m_cs_d = cs2.number_input("박스 세로(D)", min_value=0.0, value=0.0, step=1.0)
                m_cs_h = cs3.number_input("박스 높이(H)", min_value=0.0, value=0.0, step=1.0)

                st.markdown("##### 🏗️ 1파레트 입수량")
                pl1, pl2 = st.columns(2)
                m_pallet_box = pl1.number_input("파레트 당 곽 수량(개)", min_value=0, value=0)
                m_pallet_carton = pl2.number_input("파레트 당 박스 수량(개)", min_value=0, value=0)

                submitted = st.form_submit_button("제품 마스터 저장", type="primary", use_container_width=True)

                if submitted:
                    if m_code and m_name:
                        sql = """
                        INSERT INTO master_products (
                            item_code, item_name, default_purchase_price,
                            jan_box, jan_piece,
                            box_in_box, box_in_piece,
                            prod_size_w, prod_size_d, prod_size_h,
                            carton_size_w, carton_size_d, carton_size_h,
                            pallet_in_box, pallet_in_carton
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (item_code) DO UPDATE SET
                            item_name=EXCLUDED.item_name,
                            default_purchase_price=EXCLUDED.default_purchase_price,
                            jan_box=EXCLUDED.jan_box,
                            jan_piece=EXCLUDED.jan_piece,
                            box_in_box=EXCLUDED.box_in_box,
                            box_in_piece=EXCLUDED.box_in_piece,
                            prod_size_w=EXCLUDED.prod_size_w,
                            prod_size_d=EXCLUDED.prod_size_d,
                            prod_size_h=EXCLUDED.prod_size_h,
                            carton_size_w=EXCLUDED.carton_size_w,
                            carton_size_d=EXCLUDED.carton_size_d,
                            carton_size_h=EXCLUDED.carton_size_h,
                            pallet_in_box=EXCLUDED.pallet_in_box,
                            pallet_in_carton=EXCLUDED.pallet_in_carton;
                        """
                        params = (
                            m_code, m_name, m_price,
                            m_jan_box, m_jan_piece,
                            m_box_in_box, m_box_in_piece,
                            m_ps_w, m_ps_d, m_ps_h,
                            m_cs_w, m_cs_d, m_cs_h,
                            m_pallet_box, m_pallet_carton
                        )
                        if run_commit(sql, params):
                            st.success("취급 제품 상세 마스터 정보가 저장되었습니다.")
                            st.rerun()
                    else:
                        st.warning("제품 코드와 제품명은 필수 입력 항목입니다.")

        # --- Tab 2: 기존 제품 수정 및 삭제 ---
        with tab_edit:
            st.subheader("✏️ 기존 제품 정보 수정 / 삭제")
            all_products = run_query("SELECT * FROM master_products ORDER BY item_name;")
            
            if all_products:
                prod_map = {f"{p['item_name']} [{p['item_code']}]": p for p in all_products}
                selected_label = st.selectbox("수정 또는 삭제할 제품을 선택하세요", list(prod_map.keys()))
                curr_p = prod_map[selected_label]

                st.divider()
                with st.form("master_product_edit_form"):
                    st.markdown("##### 📌 기본 정보")
                    ec1, ec2, ec3 = st.columns(3)
                    e_code = ec1.text_input("제품 코드 (변경 불가)", value=curr_p['item_code'], disabled=True)
                    e_name = ec2.text_input("제품명*", value=curr_p['item_name'] or "")
                    e_price = ec3.number_input("기본 매입단가(￥)", value=float(curr_p['default_purchase_price'] or 0.0), step=10.0)

                    st.markdown("##### 🏷️ JAN 코드")
                    ej1, ej2 = st.columns(2)
                    e_jan_box = ej1.text_input("JAN 코드 (곽/소박스)", value=curr_p.get('jan_box') or "")
                    e_jan_piece = ej2.text_input("JAN 코드 (낱장/단품)", value=curr_p.get('jan_piece') or "")

                    st.markdown("##### 📦 박스 입수량")
                    eb1, eb2 = st.columns(2)
                    e_box_in_box = eb1.number_input("박스 당 곽 수량(개)", min_value=0, value=int(curr_p.get('box_in_box') or 0))
                    e_box_in_piece = eb2.number_input("박스 당 낱장 수량(개)", min_value=0, value=int(curr_p.get('box_in_piece') or 0))

                    st.markdown("##### 📐 곽(제품) 사이즈 (가로 x 세로 x 높이 mm)")
                    eps1, eps2, eps3 = st.columns(3)
                    e_ps_w = eps1.number_input("곽 가로(W)", min_value=0.0, value=float(curr_p.get('prod_size_w') or 0.0), step=1.0)
                    e_ps_d = eps2.number_input("곽 세로(D)", min_value=0.0, value=float(curr_p.get('prod_size_d') or 0.0), step=1.0)
                    e_ps_h = eps3.number_input("곽 높이(H)", min_value=0.0, value=float(curr_p.get('prod_size_h') or 0.0), step=1.0)

                    st.markdown("##### 📦 박스 사이즈 (가로 x 세로 x 높이 mm)")
                    ecs1, ecs2, ecs3 = st.columns(3)
                    e_cs_w = ecs1.number_input("박스 가로(W)", min_value=0.0, value=float(curr_p.get('carton_size_w') or 0.0), step=1.0)
                    e_cs_d = ecs2.number_input("박스 세로(D)", min_value=0.0, value=float(curr_p.get('carton_size_d') or 0.0), step=1.0)
                    e_cs_h = ecs3.number_input("박스 높이(H)", min_value=0.0, value=float(curr_p.get('carton_size_h') or 0.0), step=1.0)

                    st.markdown("##### 🏗️ 1파레트 입수량")
                    epl1, epl2 = st.columns(2)
                    e_pallet_box = epl1.number_input("파레트 당 곽 수량(개)", min_value=0, value=int(curr_p.get('pallet_in_box') or 0))
                    e_pallet_carton = epl2.number_input("파레트 당 박스 수량(개)", min_value=0, value=int(curr_p.get('pallet_in_carton') or 0))

                    btn_col1, btn_col2 = st.columns([1, 1])
                    edit_submitted = btn_col1.form_submit_button("💾 수정사항 저장", type="primary", use_container_width=True)
                    delete_submitted = btn_col2.form_submit_button("🗑️ 제품 삭제", type="secondary", use_container_width=True)

                    if edit_submitted:
                        if e_name:
                            update_sql = """
                            UPDATE master_products SET
                                item_name=%s, default_purchase_price=%s,
                                jan_box=%s, jan_piece=%s,
                                box_in_box=%s, box_in_piece=%s,
                                prod_size_w=%s, prod_size_d=%s, prod_size_h=%s,
                                carton_size_w=%s, carton_size_d=%s, carton_size_h=%s,
                                pallet_in_box=%s, pallet_in_carton=%s
                            WHERE item_code=%s;
                            """
                            update_params = (
                                e_name, e_price,
                                e_jan_box, e_jan_piece,
                                e_box_in_box, e_box_in_piece,
                                e_ps_w, e_ps_d, e_ps_h,
                                e_cs_w, e_cs_d, e_cs_h,
                                e_pallet_box, e_pallet_carton,
                                e_code
                            )
                            if run_commit(update_sql, update_params):
                                st.success(f"[{e_name}] 제품 정보가 성공적으로 수정되었습니다.")
                                st.rerun()
                        else:
                            st.warning("제품명은 필수 항목입니다.")

                    if delete_submitted:
                        if run_commit("DELETE FROM master_products WHERE item_code=%s;", (e_code,)):
                            st.warning(f"[{e_name}] 제품 마스터 정보가 삭제되었습니다.")
                            st.rerun()
            else:
                st.info("등록된 취급 제품이 없습니다.")

        st.divider()
        st.subheader("📋 취급 제품 상세 마스터 목록")
        master_list = run_query("""
            SELECT 
                item_code as 코드,
                item_name as 제품명,
                default_purchase_price as 기본매입가,
                jan_box as "JAN(곽)",
                jan_piece as "JAN(낱장)",
                box_in_box as "박스입수(곽)",
                box_in_piece as "박스입수(낱장)",
                CONCAT(prod_size_w, 'x', prod_size_d, 'x', prod_size_h) as "곽사이즈(W*D*H)",
                CONCAT(carton_size_w, 'x', carton_size_d, 'x', carton_size_h) as "박스사이즈(W*D*H)",
                pallet_in_box as "파레트입수(곽)",
                pallet_in_carton as "파레트입수(박스)"
            FROM master_products 
            ORDER BY item_name;
        """)
        if master_list:
            st.dataframe(pd.DataFrame(master_list), use_container_width=True)

    # --- 3) 입고 등록 ---
    elif menu == "📥 입고 등록" and role != "guest":
        master_products = run_query("SELECT item_code, item_name, jan_code, default_purchase_price FROM master_products ORDER BY item_name;")
        prod_options = {f"{p['item_name']} [{p['item_code']}]": p for p in master_products} if master_products else {}
        
        st.subheader("📥 입고 정보 입력")
        col1, col2, col3 = st.columns(3)
        with col1:
            in_date = st.date_input("입고 일자*", datetime.today())
            in_type = st.selectbox("매입/제공 유형*", ["매입/발주납품", "FOC무료제공"])
            
            selected_master = st.selectbox("취급 제품 선택 (선택 시 자동입력)", ["직접 입력"] + list(prod_options.keys()))
            if selected_master != "직접 입력":
                p_data = prod_options[selected_master]
                in_code = st.text_input("제품코드*", value=p_data['item_code'])
                in_name = st.text_input("제품명*", value=p_data['item_name'])
                in_jan = st.text_input("JAN 코드", value=p_data['jan_code'] or "")
                default_price = float(p_data['default_purchase_price'] or 0.0)
            else:
                in_code = st.text_input("제품코드*")
                in_name = st.text_input("제품명*")
                in_jan = st.text_input("JAN 코드")
                default_price = 0.0

        with col2:
            in_lot = st.text_input("LOT 번호*")
            in_wh = st.selectbox("입고 창고*", warehouses)
        with col3:
            in_qty = st.number_input("입고 수량*", min_value=1)
            in_price = st.number_input("매입 단가(￥)*", value=0.0 if in_type == "FOC무료제공" else default_price)

        if st.button("입고 확정", type="primary"):
            if in_code and in_name and in_lot:
                ex = run_query("SELECT id, quantity FROM inventory WHERE item_code=%s AND lot_no=%s AND warehouse=%s;", (in_code, in_lot, in_wh))
                if ex: run_commit("UPDATE inventory SET quantity=%s, purchase_price=%s WHERE id=%s;", (ex[0]['quantity']+in_qty, in_price, ex[0]['id']))
                else: run_commit("INSERT INTO inventory (item_code, item_name, jan_code, lot_no, warehouse, quantity, purchase_price) VALUES (%s, %s, %s, %s, %s, %s, %s);", (in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price))
                
                run_commit("INSERT INTO stock_movements (movement_date, movement_type, transaction_type, item_code, item_name, jan_code, lot_no, warehouse, quantity, unit_price, total_amount) VALUES (%s, 'IN', %s, %s, %s, %s, %s, %s, %s, %s, %s);", 
                           (in_date, in_type, in_code, in_name, in_jan, in_lot, in_wh, in_qty, in_price, in_qty*in_price))
                st.success("입고 완료")
                st.rerun()

    # --- 4) 출고 등록 ---
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

    # --- 5) 기간별 입출고 이력 ---
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

    # --- 6) 거래처 & 단가 관리 ---
    elif menu == "🏢 거래처 & 단가 관리" and role != "guest":
        st.subheader("➕ 신규 거래처 추가")
        new_cust = st.text_input("새 거래처명")
        if st.button("거래처 추가") and new_cust: 
            run_commit("INSERT INTO customers (customer_name) VALUES (%s);", (new_cust,))
            st.success("거래처 추가 완료")
            st.rerun()
            
        st.divider()
        
        custs = [c['customer_name'] for c in run_query("SELECT customer_name FROM customers;")]
        if custs:
            sel_c = st.selectbox("🏢 관리할 거래처 선택", custs)
            
            st.markdown(f"#### ➕ {sel_c} 신규 품목 단가 등록")
            master_prods = run_query("SELECT item_code, item_name, jan_code FROM master_products ORDER BY item_name;")
            
            col_a, col_b = st.columns(2)
            if master_prods:
                m_opts = {f"{m['item_name']} ({m['item_code']})": m for m in master_prods}
                sel_m = col_a.selectbox("취급 제품에서 선택", list(m_opts.keys()))
                target_m = m_opts[sel_m]
                p_code = target_m['item_code']
                p_name = target_m['item_name']
            else:
                col_a.info("취급 제품 마스터에 제품을 먼저 등록하시면 편리하게 선택할 수 있습니다.")
                p_code = col_a.text_input("품목코드*")
                p_name = col_a.text_input("품목명*")
                
            p_price = col_b.number_input("납품 단가(￥)*", value=0.0, key="new_p_price")
            
            if st.button("신규 단가 등록", type="primary") and p_code and p_name:
                run_commit(
                    "INSERT INTO customer_prices (customer_name, item_code, item_name, delivery_price) VALUES (%s,%s,%s,%s) ON CONFLICT (customer_name, item_code) DO UPDATE SET delivery_price=EXCLUDED.delivery_price, item_name=EXCLUDED.item_name;",
                    (sel_c, p_code, p_name, p_price)
                )
                st.success("신규 단가가 등록되었습니다.")
                st.rerun()

            st.divider()
            st.markdown(f"##### 📋 {sel_c} 등록된 품목 단가 전체 관리 (수정/삭제)")
            curr_prices = run_query("SELECT id, item_code, item_name, delivery_price FROM customer_prices WHERE customer_name=%s ORDER BY item_name;", (sel_c,))
            
            if curr_prices:
                # 테이블 헤더 표시
                h1, h2, h3, h4, h5 = st.columns([2.5, 3.5, 2, 1.2, 1.2])
                h1.caption("**품목 코드**")
                h2.caption("**품목명**")
                h3.caption("**납품 단가(￥)**")
                h4.caption("**수정**")
                h5.caption("**삭제**")

                for cp in curr_prices:
                    row_id = cp['id']
                    c_code, c_name, c_price, c_save, c_del = st.columns([2.5, 3.5, 2, 1.2, 1.2])
                    
                    # 코드, 품목명, 단가를 입력 폼 형태(text_input/number_input)로 각각 수정 가능
                    edit_code = c_code.text_input("코드", value=cp['item_code'], key=f"code_{row_id}", label_visibility="collapsed")
                    edit_name = c_name.text_input("제품명", value=cp['item_name'], key=f"name_{row_id}", label_visibility="collapsed")
                    edit_price = c_price.number_input("단가", value=float(cp['delivery_price']), key=f"price_{row_id}", label_visibility="collapsed")
                    
                    # 수정 저장 버튼
                    if c_save.button("수정", key=f"edit_{row_id}", use_container_width=True):
                        if edit_code and edit_name:
                            run_commit(
                                "UPDATE customer_prices SET item_code=%s, item_name=%s, delivery_price=%s WHERE id=%s;",
                                (edit_code, edit_name, edit_price, row_id)
                            )
                            st.success(f"[{edit_name}] 정보가 수정되었습니다.")
                            st.rerun()
                        else:
                            st.warning("코드와 제품명은 빈 칸일 수 없습니다.")
                            
                    # 삭제 버튼
                    if c_del.button("삭제", key=f"del_{row_id}", type="secondary", use_container_width=True):
                        run_commit("DELETE FROM customer_prices WHERE id=%s;", (row_id,))
                        st.warning("단가 항목이 삭제되었습니다.")
                        st.rerun()
            else:
                st.info("등록된 단가 정보가 없습니다.")

    # --- 7) 계정 관리 ---
    elif menu == "👥 계정 관리" and role == "admin":
        st.subheader("👥 계정 승인 관리")
        pending_users = run_query("SELECT username, name, role FROM users WHERE status='pending';")
        if pending_users:
            for u in pending_users:
                col1, col2, col3 = st.columns([3, 2, 2])
                col1.write(f"**아이디:** {u['username']} ({u.get('name', '이름 없음')})")
                col2.write(f"**요청 권한:** {u.get('role', 'staff')}")
                if col3.button("승인", key=f"approve_{u['username']}"):
                    run_commit("UPDATE users SET status='active' WHERE username=%s;", (u['username'],))
                    st.success(f"{u['username']} 계정이 승인되었습니다.")
                    st.rerun()
        else:
            st.info("승인 대기 중인 계정이 없습니다.")
