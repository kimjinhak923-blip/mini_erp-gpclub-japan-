import pandas as pd
import streamlit as st

st.set_page_config(page_title="대시보드", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

def get_wh_stock(prod_code, wh_name):
    return st.session_state.warehouse_stocks.get(f"{prod_code}_{wh_name}", 0)

st.header("📊 통합 대시보드")
total_items = len(st.session_state.master_products)
total_qty = 0
total_val = 0
wh_summary = {wh: 0 for wh in st.session_state.warehouses}

for p in st.session_state.master_products:
    p_code = p["code"]
    p_price = p["price"]
    for wh in st.session_state.warehouses:
        qty = get_wh_stock(p_code, wh)
        total_qty += qty
        total_val += qty * p_price
        wh_summary[wh] += qty

m1, m2, m3 = st.columns(3)
m1.metric("등록 상품 수", f"{total_items} 개")
m2.metric("총 보유 재고량", f"{total_qty:,} 개")
m3.metric("총 재고 금액 (매입가)", f"¥ {total_val:,}")

st.markdown("---")
st.subheader("🏢 창고별 재고 현황")
cols = st.columns(len(st.session_state.warehouses))
for idx, wh in enumerate(st.session_state.warehouses):
    cols[idx].info(f"**{wh}**\n\n### {wh_summary[wh]:,} 개")

st.markdown("---")
st.subheader("📦 상품별 보유 현황 (가로 통합 목록)")
dash_data = []
for p in st.session_state.master_products:
    p_code = p["code"]
    s_q = get_wh_stock(p_code, "SAGAWA")
    l_q = get_wh_stock(p_code, "L&K")
    d_q = get_wh_stock(p_code, "大吉商事")
    tot = s_q + l_q + d_q
    dash_data.append({
        "상품코드": p_code,
        "제품명": p["name"],
        "카테고리": p["category"],
        "매입단가": f"¥ {p['price']:,}",
        "SAGAWA": f"{s_q:,}",
        "L&K": f"{l_q:,}",
        "大吉商事": f"{d_q:,}",
        "총재고": f"{tot:,}",
        "총재고금액": f"¥ {tot * p['price']:,}",
    })
st.dataframe(pd.DataFrame(dash_data), use_container_width=True)
