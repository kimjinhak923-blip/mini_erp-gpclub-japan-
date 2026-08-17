import streamlit as st
import db  # 데이터베이스 모듈 불러오기

st.set_page_config(page_title="매출관리", layout="wide")

import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

user = st.session_state.get("logged_in_user")

# DB 테이블 초기화
db.init_db()

st.title("💰 매출 현황 및 분석")
st.markdown("---")

out_logs = [log for log in st.session_state.get("stock_logs", []) if log.get("type") == "출고"]

if not out_logs:
    st.info("매출(출고) 내역이 아직 없습니다.")
else:
    df_sales = pd.DataFrame(out_logs)

    total_rev = df_sales["total_amount"].sum()
    total_qty = df_sales["qty"].sum()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("총 매출액 (JPY)", f"¥{total_rev:,}")
    with c2:
        st.metric("총 출고 수량", f"{total_qty:,} 개")

    st.markdown("---")
    st.subheader("🏢 거래처별 매출 합계")
    cli_summary = (
        df_sales.groupby("client_name")[["qty", "total_amount"]]
        .sum()
        .reset_index()
    )
    st.dataframe(cli_summary, use_container_width=True)

    st.markdown("---")
    st.subheader("📦 상품별 매출 합계")
    prod_summary = (
        df_sales.groupby(["jan_code", "product_name"])[["qty", "total_amount"]]
        .sum()
        .reset_index()
    )
    st.dataframe(prod_summary, use_container_width=True)
