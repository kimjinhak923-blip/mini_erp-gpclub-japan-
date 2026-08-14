import datetime
import pytz
import streamlit as st
from sidebar_menu import render_sidebar

st.set_page_config(page_title="출퇴근시스템", layout="wide")

render_sidebar()

st.title("⏱️ 출퇴근 시스템")
st.markdown("---")

tokyo_tz = pytz.timezone("Asia/Tokyo")
now = datetime.datetime.now(tokyo_tz)

# 사용자 로그인 세션 체크 예시
if "logged_in_user" not in st.session_state:
    st.error("로그인이 필요합니다.")
    st.stop()

user = st.session_state.logged_in_user
st.subheader(f"👋 {user['name']}님, 오늘 하루도 힘내세요!")
st.info(f"📅 현재 시각: **{now.strftime('%Y-%m-%d %H:%M:%S')}** (Asia/Tokyo)")

# 출퇴근 상태 저장을 위한 세션 초기화 예시
if "clock_in_time" not in st.session_state:
    st.session_state.clock_in_time = None
if "clock_out_time" not in st.session_state:
    st.session_state.clock_out_time = None

col1, col2 = st.columns(2)

with col1:
    if st.button("☀️ 출근하기", use_container_width=True, type="primary"):
        st.session_state.clock_in_time = now.strftime("%H:%M:%S")
        # TODO: 데이터베이스(DB)에 출근 기록(user['id'], timestamp) 저장 로직 추가
        st.success(f"[{st.session_state.clock_in_time}] 출근 처리가 완료되었습니다!")

with col2:
    if st.button("🌙 퇴근하기", use_container_width=True):
        st.session_state.clock_out_time = now.strftime("%H:%M:%S")
        # TODO: 데이터베이스(DB)에 퇴근 기록(user['id'], timestamp) 저장 로직 추가
        st.warning(f"[{st.session_state.clock_out_time}] 퇴근 처리가 완료되었습니다!")

# 오늘 처리된 출퇴근 기록 현황 표시
st.markdown("---")
st.subheader("📋 오늘의 기록")
c1, c2 = st.columns(2)
c1.metric("출근 시간", st.session_state.clock_in_time or "미등록")
c2.metric("퇴근 시간", st.session_state.clock_out_time or "미등록")
