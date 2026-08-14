import streamlit as st

st.set_page_config(page_title="대시보드", layout="wide")

import datetime
import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

st.title("📊 통합 대시보드 및 매출/출고 분석")
st.markdown("---")

logs = st.session_state.get("stock_logs", [])

if not logs:
    st.info("💡 등록된 입출고 및 매출 이력이 아직 없습니다. 재고관리에서 엑셀 대량 등록 또는 개별 출고를 진행해 주세요.")
else:
    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["date"])

    # --- 상단 필터 영역 ---
    st.subheader("🔍 통합 검색 및 조건 필터")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        min_date = df["date"].min().date() if not df.empty else datetime.date.today()
        max_date = df["date"].max().date() if not df.empty else datetime.date.today()
        date_range = st.date_input("기간 선택", [min_date, max_date])

    with f_col2:
        clients = ["전체"] + list(df["client_name"].unique())
        sel_client = st.selectbox("거래처 선택", clients)

    with f_col3:
        products = ["전체"] + list(df["product_name"].unique())
        sel_product = st.selectbox("상품 선택", products)

    with f_col4:
        purposes = ["전체", "납품", "샘플", "FOC"]
        sel_purpose = st.selectbox("용도 선택", purposes)

    # 필터링 적용
    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[(filtered_df["date"].dt.date >= date_range[0]) & (filtered_df["date"].dt.date <= date_range[1])]
    if sel_client != "전체":
        filtered_df = filtered_df[filtered_df["client_name"] == sel_client]
    if sel_product != "전체":
        filtered_df = filtered_df[filtered_df["product_name"] == sel_product]
    if sel_purpose != "전체":
        filtered_df = filtered_df[filtered_df["purpose"] == sel_purpose]

    st.markdown("---")

    # --- 핵심 지표 (납품 vs 샘플+FOC 분리) ---
    out_df = filtered_df[filtered_df["type"] == "출고"]

    commercial_df = out_df[out_df["purpose"] == "납품"]
    sample_foc_df = out_df[out_df["purpose"].isin(["샘플", "FOC"])]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("총 유상 매출액 (납품)", f"¥{commercial_df['total_amount'].sum():,}")
    with m2:
        st.metric("유상 출고 수량", f"{commercial_df['qty'].sum():,} 개")
    with m3:
        st.metric("무상 출고 수량 (샘플+FOC)", f"{sample_foc_df['qty'].sum():,} 개")
    with m4:
        st.metric("샘플/FOC 환산 가치", f"¥{sample_foc_df['total_amount'].sum():,}")

    st.markdown("---")

    # --- 상세 현황 탭 ---
    tab1, tab2, tab3 = st.tabs(["🛒 용도별(납품/샘플/FOC) 상세", "🏢 거래처별 매출 현황", "📦 상품별 출고 현황"])

    with tab1:
        st.subheader("용도별 (납품 / 샘플 / FOC) 출고 내역")
        st.dataframe(
            out_df[["date", "order_no", "client_name", "product_name", "purpose", "qty", "unit_price", "total_amount", "warehouse", "status"]],
            use_container_width=True,
        )

    with tab2:
        st.subheader("거래처별 출고 및 매출 집계")
        client_summary = out_df.groupby(["client_name", "purpose"])[["qty", "total_amount"]].sum().reset_index()
        st.dataframe(client_summary, use_container_width=True)

    with tab3:
        st.subheader("상품별 출고 집계")
        product_summary = out_df.groupby(["jan_code", "product_name", "purpose"])[["qty", "total_amount"]].sum().reset_index()
        st.dataframe(product_summary, use_container_width=True)
