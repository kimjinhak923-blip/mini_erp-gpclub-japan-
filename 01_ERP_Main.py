import streamlit as st

# ⚠️ [필수] import 다음 가장 첫 번째 Streamlit 명령어로 작성되어야 합니다.
st.set_page_config(
    page_title="사내 통합 관리 시스템 (ERP)",
    page_layout="wide",
    initial_sidebar_state="expanded",
)

# --- 세션 데이터 초기화 ---
if "lang" not in st.session_state:
    st.session_state.lang = "한국어"

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "users" not in st.session_state:
    st.session_state.users = [
        {
            "id": "admin",
            "pw": "admin1234",
            "name": "관리자",
            "role": "CEO / 관리자",
            "position": "대표이사",
            "approved": True,
        },
        {
            "id": "user1",
            "pw": "1234",
            "name": "김사원",
            "role": "일반 사용자",
            "position": "사원",
            "approved": True,
        },
    ]

# --- 로그인 / 회원가입 메인 화면 ---
if not st.session_state.logged_in_user:
    st.title("🏢 사내 통합 관리 시스템")
    st.markdown("---")

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.subheader("🔐 인증 센터")
        tab_l, tab_s = st.tabs(["로그인", "회원가입"])

        with tab_l:
            login_id = st.text_input("사원번호 또는 아이디", key="main_login_id")
            login_pw = st.text_input("비밀번호", type="password", key="main_login_pw")
            if st.button("로그인", use_container_width=True, type="primary"):
                user = next((u for u in st.session_state.users if u["id"] == login_id and u["pw"] == login_pw), None)
                if user:
                    if not user.get("approved", True):
                        st.error("아직 관리자 승인이 완료되지 않은 계정입니다.")
                    else:
                        st.session_state.logged_in_user = user
                        st.switch_page("pages/01_⏱️_출퇴근시스템.py")
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

        with tab_s:
            new_id = st.text_input("아이디 (ID)", key="main_su_id")
            new_pw = st.text_input("비밀번호 (PW)", type="password", key="main_su_pw")
            new_name = st.text_input("이름 (성명)", key="main_su_name")
            if st.button("가입 신청", use_container_width=True):
                if new_id and new_pw and new_name:
                    st.session_state.users.append({
                        "id": new_id,
                        "pw": new_pw,
                        "name": new_name,
                        "role": "일반 사용자",
                        "position": "사원",
                        "approved": False,
                    })
                    st.success("회원가입 신청이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.")
                else:
                    st.error("모든 항목을 입력해주세요.")
else:
    # 이미 로그인된 경우 1번 출퇴근시스템 페이지로 이동
    st.switch_page("pages/01_⏱️_출퇴근시스템.py")
