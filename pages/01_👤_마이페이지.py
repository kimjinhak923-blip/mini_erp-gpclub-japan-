import streamlit as st

st.set_page_config(page_title="마이페이지", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다. 메인 페이지(01_ERP_Main.py)에서 로그인해 주세요.")
    st.stop()

user = st.session_state.logged_in_user
st.header("👤 마이페이지")

c1, c2 = st.columns(2)
with c1:
    st.subheader("📌 계정 정보")
    st.write(f"- **ID:** `{user['id']}`")
    st.write(f"- **Password:** `{user['pw']}`")
    st.write(f"- **Name:** {user['name']}")
    st.write(f"- **Position:** {user['position']}")
    st.write(f"- **Department:** {user['dept']}")
    st.write(f"- **Role:** {user['role']}")
with c2:
    st.subheader("🌴 근태 및 휴가 정보")
    st.write(f"- **입사일:** {user.get('hire_date', '미등록')}")
    st.metric("잔여 휴가(연차) 일수", f"{user.get('annual_leave', 15.0):.1f} 일")
