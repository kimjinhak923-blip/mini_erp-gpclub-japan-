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
                st.error("아이디/비밀번호가 올바르지 않거나 승인 대기(비활성) 중인 계정입니다.")

    with tab2:
        st.subheader("신규 계정 가입 신청")
        new_user = st.text_input("신청 아이디")
        new_pass = st.text_input("신청 비밀번호", type="password")
        new_name = st.text_input("이름")
        
        # 요청 권한 선택 (사원, 관리자, 방문자)
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
                        st.success("가입 신청이 완료되었습니다. 관리자 승인 후 로그인하실 수 있습니다.")
            else:
                st.warning("아이디와 비밀번호를 입력해주세요.")

# --- 5. 메인 ERP 화면 (로그인 성공 시) ---
else:
    role = st.session_state["role"]
    role_korean = {"admin": "관리자", "staff": "사원", "guest": "방문자"}.get(role, "방문자")
    
    # 사이드바
    st.sidebar.title("✨ GPCLUB JAPAN")
    st.sidebar.write(f"접속자: **{st.session_state['username']}** ({role_korean})")
    
    menu_options = ["🧴 재고 관리", "🛒 주문 등록", "📊 매출 현황"]
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
    # 1) 재고 관리 메뉴
    # --------------------------------------------------
    if menu == "🧴 재고 관리":
        st.subheader("제품 재고 현황 (조회)")
        inventory_data = run_query("SELECT * FROM inventory;")
        if inventory_data:
            df = pd.DataFrame(inventory_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("등록된 재고 데이터가 없습니다.")

        # 등록/수정 섹션 (사원, 관리자만 가능)
        if role in ["admin", "staff"]:
            st.divider()
            st.subheader("➕ 재고 등록 및 수정")
            col1, col2, col3 = st.columns(3)
            with col1:
                item_code = st.text_input("제품 코드")
            with col2:
                item_name = st.text_input("제품명")
            with col3:
                item_qty = st.number_input("수량", min_value=0, value=0)

            if st.button("재고 저장/수정"):
                if item_code and item_name:
                    # 기존 제품 체크 후 UPDATE 또는 INSERT
                    existing = run_query("SELECT * FROM inventory WHERE item_code=%s;", (item_code,))
                    if existing:
                        run_commit("UPDATE inventory SET item_name=%s, quantity=%s WHERE item_code=%s;", (item_name, item_qty, item_code))
                        st.success("재고 정보가 수정되었습니다.")
                    else:
                        run_commit("INSERT INTO inventory (item_code, item_name, quantity) VALUES (%s, %s, %s);", (item_code, item_name, item_qty))
                        st.success("새 재고가 등록되었습니다.")
                    st.rerun()
                else:
                    st.warning("제품 코드와 제품명을 입력하세요.")

        # 삭제 섹션 (관리자만 가능)
        if role == "admin":
            st.divider()
            st.subheader("🗑️ 재고 삭제 (관리자 전용)")
            del_code = st.text_input("삭제할 제품 코드")
            if st.button("제품 삭제"):
                if del_code:
                    run_commit("DELETE FROM inventory WHERE item_code=%s;", (del_code,))
                    st.success("제품이 삭제되었습니다.")
                    st.rerun()

    # --------------------------------------------------
    # 2) 주문 등록 메뉴
    # --------------------------------------------------
    elif menu == "🛒 주문 등록":
        if role == "guest":
            st.warning("🔒 방문자 권한은 주문을 등록하거나 수정할 수 없습니다. (조회 전용)")
        else:
            st.subheader("신규 주문 입력 및 수정")
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("제품명")
                quantity = st.number_input("수량", min_value=1, value=1)
            with col2:
                price = st.number_input("단가", min_value=0, value=1000)
                customer = st.text_input("거래처명")
                
            if st.button("주문 저장"):
                if product_name and customer:
                    run_commit(
                        "INSERT INTO orders (product_name, quantity, price, customer, order_date) VALUES (%s, %s, %s, %s, %s);",
                        (product_name, quantity, price, customer, datetime.now())
                    )
                    st.success("주문이 정상적으로 저장되었습니다.")
                    st.rerun()
                else:
                    st.warning("제품명과 거래처명을 입력하세요.")

    # --------------------------------------------------
    # 3) 매출 현황 메뉴
    # --------------------------------------------------
    elif menu == "📊 매출 현황":
        st.subheader("최근 매출 및 주문 내역 (조회)")
        orders_data = run_query("SELECT * FROM orders ORDER BY id DESC;")
        if orders_data:
            df = pd.DataFrame(orders_data)
            st.dataframe(df, use_container_width=True)

            # 주문 삭제 기능 (관리자 전용)
            if role == "admin":
                st.divider()
                st.subheader("🗑️ 주문 내역 삭제 (관리자 전용)")
                order_id_to_del = st.number_input("삭제할 주문 ID (숫자)", min_value=1, step=1)
                if st.button("주문 삭제"):
                    run_commit("DELETE FROM orders WHERE id=%s;", (order_id_to_del,))
                    st.success(f"주문 ID {order_id_to_del}번 내역이 삭제되었습니다.")
                    st.rerun()
        else:
            st.info("등록된 매출/주문 내역이 없습니다.")

    # --------------------------------------------------
    # 4) 계정 승인 및 관리 메뉴 (관리자 전용)
    # --------------------------------------------------
    elif menu == "👥 계정 승인 및 관리" and role == "admin":
        st.header("👥 계정 승인 및 권한 관리 시스템")
        
        # 1. 승인 대기 중인 계정
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
        
        # 2. 전체 계정 권한 및 상태 관리
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
                
                # 권한 변경 선택박스
                current_role_label = code_to_role.get(u['role'], "방문자")
                new_role_label = col2.selectbox(
                    "권한 변경",
                    role_options,
                    index=role_options.index(current_role_label),
                    key=f"role_sel_{u['id']}"
                )
                
                # 권한 변경 저장 버튼
                if col3.button("권한 저장", key=f"save_role_{u['id']}"):
                    new_code = role_to_code[new_role_label]
                    run_commit("UPDATE users SET role=%s WHERE id=%s;", (new_code, u['id']))
                    st.success(f"{u['username']} 님의 권한이 [{new_role_label}]로 변경되었습니다.")
                    st.rerun()
                
                # 활성/비활성화 버튼
                if u['status'] == 'active':
                    if col4.button("비활성화", key=f"deact_{u['id']}"):
                        run_commit("UPDATE users SET status='disabled' WHERE id=%s;", (u['id'],))
                        st.rerun()
                else:
                    if col4.button("활성화", key=f"act_{u['id']}"):
                        run_commit("UPDATE users SET status='active' WHERE id=%s;", (u['id'],))
                        st.rerun()
                        
                # 삭제 버튼
                if col5.button("삭제", key=f"del_{u['id']}"):
                    run_commit("DELETE FROM users WHERE id=%s;", (u['id'],))
                    st.success("계정이 삭제되었습니다.")
                    st.rerun()
        else:
            st.write("등록된 일반 계정이 없습니다.")
