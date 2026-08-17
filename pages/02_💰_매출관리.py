import datetime
import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar

st.set_page_config(page_title="매출관리", layout="wide")
render_sidebar()

# DB 테이블 초기화
db.init_db()

# --- 데이터베이스 및 세션 상태 자동 연동 ---
if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = (
        db.get_stock_logs() if hasattr(db, "get_stock_logs") else []
    )

user = st.session_state.get("logged_in_user")

st.title("💰 매출 현황 및 분석")
st.markdown("---")

# 출고 내역 추출
logs = st.session_state.get("stock_logs", [])
out_logs = [log for log in logs if log.get("type") == "출고"]

if not out_logs:
    st.info("매출(출고) 내역이 아직 없습니다.")
else:
    df_sales = pd.DataFrame(out_logs)

    # --- 데이터 연동 및 타입 안정성 보장 ---
    required_cols = {
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "type": "출고",
        "purpose": "납품",
        "product_name": "",
        "jan_code": "",
        "qty": 0,
        "total_amount": 0,
        "client_name": "",
    }
    for col, default_val in required_cols.items():
        if col not in df_sales.columns:
            df_sales[col] = default_val

    # 데이터 타입 변환 및 결측치 처리 (TypeError / KeyError 예방)
    df_sales["date"] = pd.to_datetime(df_sales["date"], errors="coerce")
    df_sales["qty"] = pd.to_numeric(df_sales["qty"], errors="coerce").fillna(0)
    df_sales["total_amount"] = pd.to_numeric(
        df_sales["total_amount"], errors="coerce"
    ).fillna(0)
    df_sales["client_name"] = df_sales["client_name"].fillna("").astype(str)
    df_sales["product_name"] = df_sales["product_name"].fillna("").astype(str)
    df_sales["jan_code"] = df_sales["jan_code"].fillna("").astype(str)
    df_sales["purpose"] = df_sales["purpose"].fillna("").astype(str)

    # 지표 집계
    total_rev = int(df_sales["total_amount"].sum())
    total_qty = int(df_sales["qty"].sum())

    # 납품(유상 매출) 전용 집계
    commercial_df = df_sales[df_sales["purpose"] == "납품"]
    comm_rev = int(
        commercial_df["total_amount"].sum()
        if not commercial_df.empty
        else total_rev
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("총 매출액 (JPY)", f"¥{total_rev:,}")
    with c2:
        st.metric("총 출고 수량", f"{total_qty:,} 개")
    with c3:
        st.metric("순 유상 매출액 (납품)", f"¥{comm_rev:,}")

    st.markdown("---")

    # --- 거래처별 매출 합계 ---
    st.subheader("🏢 거래처별 매출 합계")
    cli_summary = (
        df_sales.groupby("client_name")[["qty", "total_amount"]]
        .sum()
        .reset_index()
    )

    cli_summary["총 출고수량"] = cli_summary["qty"].apply(
        lambda x: f"{int(x):,} 개"
    )
    cli_summary["총 매출액"] = cli_summary["total_amount"].apply(
        lambda x: f"¥{int(x):,}"
    )

    show_cli = cli_summary[["client_name", "총 출고수량", "총 매출액"]].rename(
        columns={"client_name": "거래처명"}
    )
    st.dataframe(show_cli, use_container_width=True)

    st.markdown("---")

    # --- 상품별 매출 합계 ---
    st.subheader("📦 상품별 매출 합계")
    prod_summary = (
        df_sales.groupby(["jan_code", "product_name"])[
            ["qty", "total_amount"]
        ]
        .sum()
        .reset_index()
    )

    prod_summary["총 출고수량"] = prod_summary["qty"].apply(
        lambda x: f"{int(x):,} 개"
    )
    prod_summary["총 매출액"] = prod_summary["total_amount"].apply(
        lambda x: f"¥{int(x):,}"
    )

    show_prod = prod_summary[
        ["jan_code", "product_name", "총 출고수량", "총 매출액"]
    ].rename(columns={"jan_code": "JAN코드", "product_name": "상품명"})
    st.dataframe(show_prod, use_container_width=True)
