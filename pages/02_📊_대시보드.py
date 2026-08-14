import streamlit as st

st.set_page_config(page_title="대시보드", page_layout="wide")

from sidebar_menu import render_sidebar
render_sidebar()

st.title("📊 통합 대시보드")
st.markdown("---")
st.write("대시보드 화면입니다.")
