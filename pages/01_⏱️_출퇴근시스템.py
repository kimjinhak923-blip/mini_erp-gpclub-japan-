import datetime
import pytz
import streamlit as st

# ⚠️ [필수] Streamlit 명령어 중 가장 첫 번째 줄에 위치해야 함
st.set_page_config(page_title="출퇴근시스템", page_layout="wide")

# 사이드바 모듈 import 및 실행
from sidebar_menu import render_sidebar

render_sidebar()

# --- 이하 페이지 본문 코드 ---
st.title("⏱️ 출퇴근 시스템")
st.markdown("---")

tokyo_tz = pytz.timezone("Asia/Tokyo")
now = datetime.datetime.now(tokyo_tz)

user = st.session_state.logged_in_user
st.subheader(f"👋 {user['name']}님, 오늘 하루도 힘내세요!")
st.info(f"📅 현재 시각: **{now.strftime('%Y-%m-%d %H:%M:%S')}** (Asia/Tokyo)")

col1, col2 = st.columns(2)

with col1:
    if st.button("☀️ 출근하기", use_container_width=True, type="primary"):
        st.success(f"[{now.strftime('%H:%M:%S')}] 출근 처리가 완료되었습니다!")

with col2:
    if st.button("🌙 퇴근하기", use_container_width=True):
        st.warning(f"[{now.strftime('%H:%M:%S')}] 퇴근 처리가 완료되었습니다!")
