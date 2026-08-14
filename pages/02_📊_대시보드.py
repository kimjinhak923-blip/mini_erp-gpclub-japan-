import streamlit as st

st.set_page_config(page_title="대시보드", page_layout="wide")

import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

st.title("📊 통합 대시보드")
st.markdown("---")

total_p = len(st.session_state.get("master_products", []))
total_clients = len(st.session_state.get("clients", []))
total_logs = len(st.session_state.get("stock_logs", []))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("등록 마스터 상품 수", f"{total_p} 개")
with c2:
    st.metric("등록 거래처 수", f"{total_clients} 개")
with c3:
    st.metric("누적 입출고 건수", f"{total_logs} 건")

st.markdown("---")
st.subheader("📦 창고별 현재 재고 현황")
if st.session_state.get("warehouse_stocks"):
    st.dataframe(pd.DataFrame(st.session_state.warehouse_stocks), use_container_width=True)
else:
    st.info("재고 데이터가 존재하지 않습니다.")
