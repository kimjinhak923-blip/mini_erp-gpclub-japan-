import pandas as pd
import streamlit as st

user = st.session_state.get("logged_in_user")

st.title("📊 통합 대시보드")
st.markdown("---")

if not user:
    st.warning("로그인이 필요한 페이지입니다. 메인 페이지에서 먼저 로그인해 주세요.")
else:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("총 마스터 상품", f"{len(st.session_state.master_products)} 개")
    with c2:
        total_qty = sum(item["stock_qty"] for item in st.session_state.warehouse_stocks)
        st.metric("총 재고 수량", f"{total_qty:,} 개")
    with c3:
        st.metric("등록 거래처", f"{len(st.session_state.clients)} 개")
    with c4:
        total_sales = sum(
            log.get("total_amount", 0)
            for log in st.session_state.stock_logs
            if log.get("type") == "출고"
        )
        st.metric("누적 총 매출", f"¥{total_sales:,}")

    st.markdown("---")
    st.subheader("🏢 창고별 재고 분포")
    if st.session_state.warehouse_stocks:
        df_stocks = pd.DataFrame(st.session_state.warehouse_stocks)
        st.dataframe(df_stocks, use_container_width=True)
    else:
        st.info("재고 데이터가 없습니다.")

    st.markdown("---")
    st.subheader("📦 전체 마스터 상품 목록")
    if st.session_state.master_products:
        df_master = pd.DataFrame(st.session_state.master_products)
        st.dataframe(df_master, use_container_width=True)
    else:
        st.info("마스터 상품 데이터가 없습니다.")
