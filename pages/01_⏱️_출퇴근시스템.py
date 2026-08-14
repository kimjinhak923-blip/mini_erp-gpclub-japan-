import streamlit as st
from sidebar_menu import render_sidebar
from utils.i18n import render_live_clock, txt

# 1. 공통 사이드바 및 언어선택기 호출
render_sidebar()

# 2. 페이지 헤더 및 실시간 시계
st.title(txt("menu_commute", "⏱️ 출퇴근 관리 / 타임카드"))
render_live_clock()

# ... (이하 기존 출퇴근 로직 코드)

# ⚠️ 최상단 배치로 Streamlit Cloud Execution Error 방지
st.set_page_config(page_title="출퇴근시스템", layout="wide")

# 사이드바 렌더링 (로그인 미수행 시 여기서 st.stop())
render_sidebar()

st.title(txt("commute_system"))
st.markdown("---")

tokyo_tz = pytz.timezone("Asia/Tokyo")
now = datetime.datetime.now(tokyo_tz)

user = st.session_state.logged_in_user
st.subheader(txt("greeting", name=user['name']))

# 상단 실시간 시계 컴포넌트 출력
col_time1, col_time2 = st.columns([2, 1])
with col_time1:
    st.info(f"{txt('current_time_info')}")
with col_time2:
    render_live_clock()

# 세션 내 출퇴근 기록 저장용 초기화
if "clock_in_time" not in st.session_state:
    st.session_state.clock_in_time = None
if "clock_out_time" not in st.session_state:
    st.session_state.clock_out_time = None

col1, col2 = st.columns(2)

with col1:
    if st.button(txt("clock_in"), use_container_width=True, type="primary"):
        st.session_state.clock_in_time = now.strftime("%H:%M:%S")
        st.success(txt("clock_in_success", time=st.session_state.clock_in_time))

with col2:
    if st.button(txt("clock_out"), use_container_width=True):
        st.session_state.clock_out_time = now.strftime("%H:%M:%S")
        st.warning(txt("clock_out_success", time=st.session_state.clock_out_time))

st.markdown("---")
st.subheader(txt("todays_record"))
c1, c2 = st.columns(2)
c1.metric(txt("clock_in_time"), st.session_state.clock_in_time or txt("unregistered"))
c2.metric(txt("clock_out_time"), st.session_state.clock_out_time or txt("unregistered"))
