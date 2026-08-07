import streamlit as st
import psycopg2
import pandas as pd
import io

# DB 연결 설정 (본인 환경에 맞게 수정하세요)
DB_CONFIG = {
    "host": "localhost",
    "database": "mini_erp_db",
    "user": "postgres",
    "password": "your_password",  # pgAdmin 비밀번호
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def to_excel(df):
    """Dataframe을 엑셀 파일 바이너리로 변환"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ERP_Data')
    processed_data = output.getvalue()
    return processed_data

st.set_page_config(page_title="5인 소기업 미니 ERP", layout="wide", page_icon="💼")

# 세션 상태 초기화 (로그인 정보 저장)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.full_name = ""
    st.session_state.role = ""

# --- 1. 로그인 / 로그아웃 화면 ---
if not st.session_state.logged_in:
    st.title("💼 소기업 미니 ERP - 로그인")
    
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submit_login = st.form_submit_button("로그인")
        
        if submit_login:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "SELECT username, full_name, role FROM users WHERE username = %s AND password = %s",
                    (username, password)
                )
                user = cur.fetchone()
                conn.close()
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[0]
                    st.session_state.full_name = user[1]
                    st.session_state.role = user[2]
                    st.success(f"환영합니다, {user[1]}님!")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
            except Exception as e:
                st.error(f"DB 연결 오류: {e}DB 설정과 pgAdmin 4 실행 여부를 확인하세요.")

else:
    # 로그인 성공 후 메인 화면
    st.sidebar.markdown(f"### 👤 접속자: **{st.session_state.full_name}** ({st.session_state.role})")
    if st.sidebar.button("🚪 로그아웃"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.full_name = ""
        st.session_state.role = ""
        st.rerun()

    st.sidebar.divider()
    
    menu_options = ["📦 재고 관리", "🛒 주문 등록", "📊 매출 현황 및 엑셀 다운로드"]
    if st.session_state.role == "ADMIN":
        menu_options.append("👥 직원 계정 관리")
        
    menu = st.sidebar.radio("메뉴 선택", menu_options)
    
    st.title("💼 5인 소기업 미니 ERP")

    # --- 2. 재고 관리 메뉴 ---
    if menu == "📦 재고 관리":
        st.header("📦 상품 및 재고 관리")
        
        # 상품 등록 폼
        with st.expander("➕ 새 상품 등록하기", expanded=True):
            with st.form("add_product_form"):
                col1, col2, col3, col4 = st.columns(4)
                code = col1.text_input("상품 코드 (예: P004)")
                name = col2.text_input("상품명")
                price = col3.number_input("단가 (원)", min_value=0, step=1000)
                stock = col4.number_input("초기 재고 (개)", min_value=0, step=1)
                submit = st.form_submit_button("상품 등록")

                if submit:
                    if code and name:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO products (product_code, product_name, price, stock_quantity) VALUES (%s, %s, %s, %s)",
                                (code, name, price, stock)
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"'{name}' 상품이 성공적으로 등록되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"등록 실패: {e}")
                    else:
                        st.warning("상품 코드와 상품명을 입력해주세요.")

        # 상품 목록 조회 및 엑셀 다운로드
        st.subheader("📋 현재고 목록")
        conn = get_connection()
        df_products = pd.read_sql(
            "SELECT product_id AS ID, product_code AS 코드, product_name AS 상품명, price AS 단가, stock_quantity AS 재고수량 FROM products ORDER BY product_id DESC", 
            conn
        )
        conn.close()
        
        st.dataframe(df_products, use_container_width=True)
        
        if not df_products.empty:
            excel_data = to_excel(df_products)
            st.download_button(
                label="📥 재고 현황 엑셀 다운로드",
                data=excel_data,
                file_name="재고현황.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- 3. 주문 등록 메뉴 ---
    elif menu == "🛒 주문 등록":
        st.header("🛒 주문 등록 및 출고")
        
        conn = get_connection()
        products_df = pd.read_sql("SELECT product_id, product_name, price, stock_quantity FROM products WHERE stock_quantity > 0", conn)
        conn.close()

        if products_df.empty:
            st.warning("등록된 상품이 없거나 모든 상품의 재고가 부족합니다. 먼저 재고를 추가해주세요.")
        else:
            product_dict = {f"{row['product_name']} (단가: {row['price']:,.0f}원 / 재고: {row['stock_quantity']}개)": row for _, row in products_df.iterrows()}
            selected_p_name = st.selectbox("상품 선택", list(product_dict.keys()))
            selected_p = product_dict[selected_p_name]

            with st.form("order_form"):
                customer = st.text_input("고객사/거래처명")
                qty = st.number_input("주문 수량", min_value=1, max_value=int(selected_p['stock_quantity']), step=1)
                submit_order = st.form_submit_button("주문 및 출고 완료")

                if submit_order:
                    if customer:
                        total = qty * float(selected_p['price'])
                        conn = get_connection()
                        cur = conn.cursor()
                        
                        # 주문 저장
                        cur.execute(
                            "INSERT INTO orders (product_id, customer_name, quantity, total_price, created_by) VALUES (%s, %s, %s, %s, %s)",
                            (selected_p['product_id'], customer, qty, total, st.session_state.username)
                        )
                        # 재고 차감
                        cur.execute(
                            "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                            (qty, selected_p['product_id'])
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"'{customer}'님 주문이 완료되었습니다. (결제 금액: {total:,.0f}원)")
                        st.rerun()
                    else:
                        st.warning("거래처명을 입력해주세요.")

    # --- 4. 매출 현황 및 엑셀 다운로드 메뉴 ---
    elif menu == "📊 매출 현황 및 엑셀 다운로드":
        st.header("📊 매출 현황 및 내역 분석")
        
        conn = get_connection()
        query = """
            SELECT o.order_id AS 주문번호, o.order_date AS 일시, o.customer_name AS 거래처, 
                   p.product_name AS 상품명, o.quantity AS 수량, o.total_price AS 총금액,
                   o.created_by AS 담당자
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            ORDER BY o.order_id DESC
        """
        df_orders = pd.read_sql(query, conn)
        conn.close()

        if not df_orders.empty:
            col1, col2 = st.columns(2)
            col1.metric("총 누적 매출액", f"{df_orders['총금액'].sum():,.0f} 원")
            col2.metric("총 주문 건수", f"{len(df_orders)} 건")
            
            st.divider()
            
            st.subheader("📋 전체 주문 내역")
            st.dataframe(df_orders, use_container_width=True)
            
            # 엑셀 다운로드 버튼
            excel_data = to_excel(df_orders)
            st.download_button(
                label="📥 매출 내역 전체 엑셀 다운로드",
                data=excel_data,
                file_name="매출내역_전체.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("아직 등록된 주문 내역이 없습니다.")

    # --- 5. 직원 계정 관리 (관리자 전용) ---
    elif menu == "👥 직원 계정 관리":
        st.header("👥 직원 계정 및 권한 관리 (관리자전용)")
        
        with st.expander("➕ 새 직원 계정 추가"):
            with st.form("add_user_form"):
                new_user = st.text_input("아이디")
                new_pass = st.text_input("비밀번호", type="password")
                new_name = st.text_input("이름")
                new_role = st.selectbox("권한", ["STAFF", "ADMIN"])
                submit_user = st.form_submit_button("계정 생성")
                
                if submit_user:
                    if new_user and new_pass and new_name:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO users (username, password, full_name, role) VALUES (%s, %s, %s, %s)",
                                (new_user, new_pass, new_name, new_role)
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"직원 '{new_name}' 계정이 생성되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"계정 생성 실패: {e}")
                    else:
                        st.warning("모든 필드를 입력해주세요.")
                        
        st.subheader("📋 등록된 직원 목록")
        conn = get_connection()
        df_users = pd.read_sql("SELECT user_id AS ID, username AS 아이디, full_name AS 이름, role AS 권한, created_at AS 생성일 FROM users", conn)
        conn.close()
        st.dataframe(df_users, use_container_width=True)
