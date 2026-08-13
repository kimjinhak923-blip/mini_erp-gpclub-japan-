import streamlit as st

st.set_page_config(page_title="마이페이지", layout="wide")

from sidebar_menu import render_sidebar

render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("👤 마이페이지")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("📋 기본 정보")
    st.write(f"**아이디:** {user['id']}")
    st.write(f"**이름:** {user['name']}")
    st.write(f"**직급:** {user.get('position', '사원')}")
    st.write(f"**시스템 권한:** {user.get('role', '일반 사용자')}")

with col2:
    st.subheader("🌴 근태 및 연차 정보")
    st.write(f"**입사일:** {user.get('hire_date', '미등록')}")
    st.write(f"**잔여 연차:** {user.get('remaining_leave', 0)} 일")

st.markdown("---")
st.subheader("🔑 비밀번호 변경")
with st.form("change_pw_form"):
    current_pw = st.text_input("현재 비밀번호", type="password")
    new_pw = st.text_input("새 비밀번호", type="password")
    new_pw_confirm = st.text_input("새 비밀번호 확인", type="password")
    submit_pw = st.form_submit_button("비밀번호 변경")

    if submit_pw:
        if current_pw != user["pw"]:
            st.error("현재 비밀번호가 일치하지 않습니다.")
        elif new_pw != new_pw_confirm:
            st.error("새 비밀번호 확인이 일치하지 않습니다.")
        elif not new_pw:
            st.error("새 비밀번호를 입력해 주세요.")
        else:
            user["pw"] = new_pw
            st.success("비밀번호가 성공적으로 변경되었습니다.")
