import hashlib
import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="통합 ERP 시스템", layout="wide")

# 1. Supabase 클라이언트 설정 (st.secrets 사용)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("st.secrets에 SUPABASE_URL 또는 SUPABASE_KEY 설정이 누락되었습니다.")

# 비밀번호 SHA-256 해시 함수
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# 자동 로그인 세션 복구 함수
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
# 🔍 [디버그 영역] DB 데이터 수신 상태 실시간 점검 (사이드바)
# =========================================================
st.sidebar.markdown("---")
with st.sidebar.expander("🛠️ DB 연결 디버거", expanded=True):
    try:
        debug_res = supabase.table("user_profiles").select("*").execute()
        st.caption("📌 DB 조회 결과:")
        st.write(debug_res.data)
        
        if not debug_res.data:
            st.warning("⚠️ DB에서 가져온 데이터가 빈 배열(`[]`)입니다.\n- Supabase RLS 권한 문제이거나\n- 테이블 데이터가 비어있습니다.")
        else:
            st.success(f"✅ DB 연동 성공! ({len(debug_res.data)}건 조회됨)")
    except Exception as e:
        st.error(f"❌ DB 연동 오류: {e}")
st.sidebar.markdown("---")

# =========================================================
# 🔑 로그인 / 회원가입 화면
# =========================================================
if "user" not in st.session_state:
    st.title("🏢 통합 ERP 시스템")
    
    tab1, tab2 = st.tabs(["🔑 로그인", "📝 회원가입 신청"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("아이디", value="admin")
            password = st.text_input("비밀번호", type="password", value="admin123!")
            submitted = st.form_submit_button("로그인")
            
            if submitted:
                hashed_pw = hash_password(password)
                try:
                    res = supabase.table("user_profiles").select("*") \
                        .eq("username", username) \
                        .eq("password_hash", hashed_pw) \
                        .execute()
                    
                    if res.data:
                        user = res.data[0]
                        if user.get("status") == "PENDING":
                            st.warning("⏳ 관리자 승인 대기 중인 계정입니다.")
                        elif user.get("status") == "REJECTED":
                            st.error("❌ 가입이 거절된 계정입니다.")
                        elif user.get("is_active") == False:
                            st.error("❌ 비활성화된 계정입니다.")
                        else:
                            st.session_state["user"] = user
                            st.query_params["session_token"] = user["id"]
                            st.success(f"{user['full_name']}님 환영합니다!")
                            st.rerun()
                    else:
                        st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")
                except Exception as e:
                    st.error(f"로그인 처리 중 오류 발생: {e}")
                    
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
            
            signup_submitted = st.form_submit_button("가입 신청")
            
            if signup_submitted and new_username and new_password and full_name:
                hashed_pw = hash_password(new_password)
                selected_role = role_map[role_display]
                try:
                    supabase.table("user_profiles").insert({
                        "username": new_username,
                        "password_hash": hashed_pw,
                        "full_name": full_name,
                        "role": selected_role,
                        "status": "PENDING",
                        "is_active": True
                    }).execute()
                    st.success("가입 신청이 완료되었습니다. 관리자 승인 후 이용 가능합니다.")
                except Exception as e:
                    st.error(f"가입 신청 실패: {e}")

# =========================================================
# 📊 메인 시스템 화면 (로그인 성공 시)
# =========================================================
else:
    user = st.session_state["user"]
    role_label = {
        "ADMIN": "👑 관리자",
        "STAFF": "👔 사원",
        "GUEST": "👀 방문자"
    }.get(user["role"], user["role"])
    
    st.sidebar.title(f"{role_label} {user['full_name']}님")
    
    if st.sidebar.button("🚪 로그아웃"):
        del st.session_state["user"]
        st.query_params.clear()
        st.rerun()
        
    st.title(f"🎉 ERP 시스템 메인 화면 ({role_label})")
    st.success(f"{user['full_name']}님, 로그인에 성공하셨습니다!")
