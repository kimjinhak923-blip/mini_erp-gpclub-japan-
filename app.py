import hashlib
import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="통합 ERP 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 1. Supabase 클라이언트 설정
# =========================================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("st.secrets에 SUPABASE_URL 또는 SUPABASE_KEY 설정이 누락되었습니다.")

# 비밀번호 SHA-256 해시 함수
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# 자동 로그인 세션 복구
def check_auto_login():
    if "user" not in st.session_state and "session_token" in st.query_params:
        user_id = st.query_params["session_token"]
        try:
            res = supabase.table("user_profiles").select("*").eq("id", user_id).eq("status", "APPROVED").execute()
            if res.data:
                st.session_state["user"] = res.data[0]
        except Exception:
            st.query_params.clear()

check_auto_login()

# =========================================================
# 🔑 2. 로그인 / 회원가입 화면
# =========================================================
if "user" not in st.session_state:
    st.title("🏢 통합 ERP 시스템")
    
    tab1, tab2 = st.tabs(["🔑 로그인", "📝 회원가입 신청"])
    
    # --- 로그인 탭 ---
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
                    res = supabase.table("user_profiles") \
                        .select("*") \
                        .eq("username", clean_username) \
                        .execute()
                    
                    if not res.data:
                        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                    else:
                        user = res.data[0]
                        db_hash = user.get("password_hash", "")
                        
                        if db_hash != hashed_pw:
                            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                        elif user.get("status") == "PENDING":
                            st.warning("⏳ 관리자 승인 대기 중인 계정입니다.")
                        elif user.get("status") == "REJECTED":
                            st.error("❌ 가입 신청이 거절된 계정입니다.")
                        elif user.get("is_active") == False:
                            st.error("❌ 비활성화된 계정입니다.")
                        else:
                            st.session_state["user"] = user
                            st.query_params["session_token"] = user["id"]
                            st.success(f"🎉 {user['full_name']}님 환영합니다!")
                            st.rerun()

                except Exception as e:
                    st.error(f"로그인 처리 중 오류 발생: {e}")
                    
    # --- 회원가입 탭 ---
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("신청할 아이디")
            new_password = st.text_input("신청할 비밀번호", type="password")
            full_name = st.text_input("이름")
            
            role_display = st.selectbox(
                "희망 권한 선택",
                ["방문자 (조회만 가능)", "사원 (등록/수정 가능)", "관리자 (전체 관리)"]
            )
            role_map = {
                "방문자 (조회만 가능)": "GUEST",
                "사원 (등록/수정 가능)": "STAFF",
                "관리자 (전체 관리)": "ADMIN"
            }
            
            signup_submitted = st.form_submit_button("가입 신청", use_container_width=True)
            
            if signup_submitted and new_username and new_password and full_name:
                clean_new_username = new_username.strip()
                clean_new_pw = new_password.strip()
                hashed_pw = hash_password(clean_new_pw)
                selected_role = role_map[role_display]
                
                try:
                    supabase.table("user_profiles").insert({
                        "username": clean_new_username,
                        "password_hash": hashed_pw,
                        "full_name": full_name.strip(),
                        "role": selected_role,
                        "status": "PENDING",
                        "is_active": True
                    }).execute()
                    st.success("가입 신청이 완료되었습니다. 관리자 승인 후 이용 가능합니다.")
                except Exception as e:
                    st.error(f"가입 신청 실패: {e}")

# =========================================================
# 📊 3. 메인 시스템 화면 (카테고리 메뉴 구성)
# =========================================================
else:
    user = st.session_state["user"]
    user_role = user.get("role", "GUEST")
    
    role_label = {
        "ADMIN": "👑 최고 관리자",
        "STAFF": "👔 일반 사원",
        "GUEST": "👀 방문자"
    }.get(user_role, user_role)
    
    # --- 사이드바 프로필 & 로그아웃 ---
    st.sidebar.title("🏢 ERP 시스템")
    st.sidebar.subheader(f"{user['full_name']} 님")
    st.sidebar.caption(f"권한: {role_label}")
    st.sidebar.write(f"아이디: `{user['username']}`")
    
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        del st.session_state["user"]
        st.query_params.clear()
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # --- 권한에 따른 사이드바 카테고리 메뉴 정의 ---
    menu_options = ["📊 대시보드", "📦 재고 관리", "📈 매출 / 영업 관리"]
    
    # 관리자 전용 메뉴 추가
    if user_role == "ADMIN":
        menu_options.append("👥 사용자 / 승인 관리")
        menu_options.append("⚙️ 시스템 설정")
        
    selected_menu = st.sidebar.radio("📌 카테고리 메뉴", menu_options)

    # --- 카테고리별 화면 렌더링 ---
    st.title(f"{selected_menu}")
    st.caption(f"현재 접속 계정: {user['full_name']} ({role_label})")
    st.markdown("---")
    
    # 1. 대시보드
    if selected_menu == "📊 대시보드":
        st.header("📊 시스템 요약 대시보드")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="총 재고 수량", value="1,240 개", delta="12 개 증가")
        col2.metric(label="이번 달 매출", value="₩ 45,200,000", delta="8.5%")
        col3.metric(label="신규 가입 대기", value="3 명", delta="-1 명")
        col4.metric(label="시스템 상태", value="정상 (OK)", delta_color="normal")
        
        st.subheader("📌 최근 업무 공지 사항")
        st.info("• 월말 재고 조사 일정 안내: 이번 주 금요일 18:00 진행 예정\n• 시스템 보안 점검 완료")

    # 2. 재고 관리
    elif selected_menu == "📦 재고 관리":
        st.header("📦 품목 및 재고 현황")
        
        c1, c2 = st.columns([3, 1])
        search_kw = c1.text_input("품목명 검색", placeholder="검색어를 입력하세요...")
        if user_role in ["ADMIN", "STAFF"]:
            c2.button("➕ 신규 품목 등록", use_container_width=True)
            
        st.table([
            {"품목코드": "ITEM-001", "품목명": "사무용 의자", "수량": 45, "단가": "120,000원", "상태": "정상"},
            {"품목코드": "ITEM-002", "품목명": "27인치 모니터", "수량": 12, "단가": "350,000원", "상태": "재고 부족"},
            {"품목코드": "ITEM-003", "품목명": "무선 키보드", "수량": 88, "단가": "45,000원", "상태": "정상"},
        ])

    # 3. 매출 / 영업 관리
    elif selected_menu == "📈 매출 / 영업 관리":
        st.header("📈 영업 및 매출 실적")
        st.subheader("월별 매출 그래프")
        
        chart_data = {
            "1월": 3200, "2월": 4100, "3월": 3800, "4월": 5100, "5월": 4520
        }
        st.bar_chart(chart_data)

    # 4. 사용자 / 승인 관리 (ADMIN 전용)
    elif selected_menu == "👥 사용자 / 승인 관리":
        st.header("👥 사용자 계정 및 가입 승인 관리")
        
        st.subheader("📋 전체 사용자 목록 (Supabase 동기화)")
        try:
            users_res = supabase.table("user_profiles").select("id, username, full_name, role, status, is_active, created_at").execute()
            if users_res.data:
                st.dataframe(users_res.data, use_container_width=True)
            else:
                st.write("등록된 사용자가 없습니다.")
        except Exception as e:
            st.error(f"사용자 목록 불러오기 실패: {e}")

    # 5. 시스템 설정 (ADMIN 전용)
    elif selected_menu == "⚙️ 시스템 설정":
        st.header("⚙️ 시스템 환경 설정")
        st.checkbox("신규 가입 알림 받기", value=True)
        st.checkbox("다크 모드 기본 적용", value=False)
        st.button("💾 설정 저장", type="primary")
