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

# --- 2. DB 연결 함수 ---
def get_connection():
    try:
        # Streamlit Secrets 또는 기본 설정값 연결
        return psycopg2.connect(
            host=st.secrets.get("DB_HOST", "localhost"),
            database=st.secrets.get("DB_NAME", "postgres"),
            user=st.secrets.get("DB_USER", "postgres"),
            password=st.secrets.get("DB_PASSWORD", "admin123"),
            port=st.secrets.get("DB_PORT", "5432")
        )
    except Exception as e:
        st.error(f"DB 연결 오류: {e}\nSupabase 또는 DB 접속 설정을 확인하세요.")
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
    st.session_state["role"] = "staff"

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
                st.success(f"환영합니다, {user[0]['username']}님!")
                st.rerun()
            else:
                st.error("아이디/비밀번호가 올바르지 않거나 승인 대기(비활성) 중인 계정입니다.")

    with tab2:
        st.subheader("신규 계정 가입 신청")
        new_user = st.text_input("신청 아이디")
        new_pass = st.text_input("신청 비밀번호", type="password")
        new_name = st.text_input("이름")
        req_role = st.selectbox("요청 권한", ["staff", "admin"])
        
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
                        st.success("가입 신청이 완료되었습니다! 관리자 승인 후 로그인할 수 있습니다.")
            else:
                st.warning("아이디와 비밀번호를 입력해주세요.")

# --- 5. 메인 ERP 화면 (로그인 성공 시) ---
else:
    # 사이드바
    st.sidebar.title("✨ GPCLUB JAPAN")
    st.sidebar.write(f"접속자: **{st.session_state['username']}** ({st.session_state['role']})")
    
    menu_options = ["🧴 재고 관리", "🛒 주문 등록", "📊 매출 현황"]
    if st.session_state["role"] == "admin":
        menu_options.append("👥 계정 승인 및 관리")
        
    menu = st.sidebar.radio("메뉴 선택", menu_options)
    
    if st.sidebar.button("로그아웃"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = "staff"
        st.rerun()

    st.title(f"✨ GPCLUB JAPAN ERP - {menu}")

    # 1) 재고 관리 메뉴
    if menu == "🧴 재고 관리":
        st.subheader("제품 재고 현황")
        inventory_data = run_query("SELECT * FROM inventory;")
        if inventory_data:
            df = pd.DataFrame(inventory_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("등록된 재고 데이터가 없습니다.")

    # 2) 주문 등록 메뉴
    elif menu == "🛒 주문 등록":
        st.subheader("신규 주문 입력")
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("제품명")
            quantity = st.number_input("수량", min_value=1, value=1)
        with col2:
            price = st.number_input("단가 (엔/원)", min_value=0, value=1000)
            customer = st.text_input("거래처명")
            
        if st.button("주문 저장"):
            run_commit(
                "INSERT INTO orders (product_name, quantity, price, customer, order_date) VALUES (%s, %s, %s, %s, %s);",
                (product_name, quantity, price, customer, datetime.now())
            )
            st.success("주문이 정상적으로 등록되었습니다.")

    # 3) 매출 현황 메뉴
    elif menu == "📊 매출 현황":
        st.subheader("최근 매출 및 주문 내역")
        orders_data = run_query("SELECT * FROM orders ORDER BY order_date DESC;")
        if orders_data:
            df = pd.DataFrame(orders_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("등록된 매출/주문 내역이 없습니다.")

    # 4) 계정 승인 및 관리 메뉴 (관리자 전용)
    elif menu == "👥 계정 승인 및 관리":
        st.header("👥 계정 승인 및 관리 시스템")
        
        # 승인 대기 중인 계정
        st.subheader("⏳ 승인 대기 신청 (Pending)")
        pending_users = run_query("SELECT id, username, name, role FROM users WHERE status='pending';")
        
        if pending_users:
            for u in pending_users:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                col1.write(f"**{u['username']}** ({u['name']})")
                col2.write(f"요청권한: {u['role']}")
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
        
        # 전체 계정 목록
        st.subheader("⚙️ 전체 직원 계정 목록 및 상태 변경")
        all_users = run_query("SELECT id, username, name, role, status FROM users WHERE username != 'admin';")
        
        if all_users:
            for u in all_users:
                col1, col2, col3 = st.columns([3, 1, 1])
                status_icon = "🟢 활성" if u['status'] == 'active' else "🔴 비활성"
                col1.write(f"**{u['username']}** ({u['name']}) - 권한: {u['role']} [{status_icon}]")
                
                if u['status'] == 'active':
                    if col2.button("비활성화", key=f"deact_{u['id']}"):
                        run_commit("UPDATE users SET status='disabled' WHERE id=%s;", (u['id'],))
                        st.rerun()
                else:
                    if col2.button("활성화", key=f"act_{u['id']}"):
                        run_commit("UPDATE users SET status='active' WHERE id=%s;", (u['id'],))
                        st.rerun()
                        
                if col3.button("삭제", key=f"del_{u['id']}"):
                    run_commit("DELETE FROM users WHERE id=%s;", (u['id'],))
                    st.success("계정이 삭제되었습니다.")
                    st.rerun()
        else:
            st.write("등록된 일반 직원 계정이 없습니다.")
