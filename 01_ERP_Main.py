import streamlit as st
import pandas as pd
from utils.db_client import supabase
from utils.auth import require_auth

# Streamlit 설정은 최상단에 배치
st.set_page_config(page_title="ERP System", page_icon="🏢", layout="wide")

# 로그인 인증 수행 (미인증 시 여기서 화면이 멈추고 로그인 화면 표시)
require_auth()

# --- 이 아래부터 기존 페이지 기능 코드 작성 ---

st.set_page_config(
    page_title="통합 ERP 시스템 - Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 통합 ERP Dashboard")
st.caption("GitHub + Supabase + Streamlit 기반 대기업 표준 ERP")

# 1. Top KPI Metrics
st.markdown("### 📈 주요 업무 KPI")
col1, col2, col3, col4 = st.columns(4)

try:
    # B2B 매출
    sales_res = supabase.table("sales_orders").select("total_amount").execute()
    total_sales = sum([item['total_amount'] for item in sales_res.data]) if sales_res.data else 0

    # 미청구 금액 (Invoice 미연결 Delivery)
    unbilled_res = supabase.table("deliveries").select("shipping_fee").filter("invoice_id", "is", "null").filter("status", "eq", "COMPLETED").execute()
    unbilled_amount = sum([item['shipping_fee'] for item in unbilled_res.data]) if unbilled_res.data else 0

    # 현재 재고 수량
    inv_res = supabase.table("inventories").select("quantity").execute()
    total_inv = sum([item['quantity'] for item in inv_res.data]) if inv_res.data else 0

    # EC 매출액
    ec_res = supabase.table("ec_sales").select("amount").execute()
    total_ec = sum([item['amount'] for item in ec_res.data]) if ec_res.data else 0

except Exception as e:
    total_sales, unbilled_amount, total_inv, total_ec = 0, 0, 0, 0

col1.metric("총 B2B 매출 (SO)", f"₩{total_sales:,.0f}")
col2.metric("미청구 배송비/건", f"₩{unbilled_amount:,.0f}")
col3.metric("현재 총 창고 재고", f"{total_inv:,} 개")
col4.metric("EC 총 매출액", f"¥{total_ec:,.0f}")

st.divider()

# 2. 최근 트랜잭션 현황
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🛒 최근 구매 발주 (Purchase Orders)")
    try:
        po_data = supabase.table("purchase_orders").select("supplier_po_no, order_date, status, total_amount").order("created_at", desc=True).limit(5).execute()
        if po_data.data:
            st.dataframe(pd.DataFrame(po_data.data), use_container_width=True)
        else:
            st.info("등록된 구매 발주 건이 없습니다.")
    except Exception as e:
        st.error("구매 발주 데이터를 불러올 수 없습니다.")

with col_right:
    st.subheader("📦 최근 납품 건 (Deliveries)")
    try:
        del_data = supabase.table("deliveries").select("delivery_no, delivery_date, status, deal_type, shipping_fee").order("created_at", desc=True).limit(5).execute()
        if del_data.data:
            st.dataframe(pd.DataFrame(del_data.data), use_container_width=True)
        else:
            st.info("등록된 납품 건이 없습니다.")
    except Exception as e:
        st.error("납품 데이터를 불러올 수 없습니다.")
