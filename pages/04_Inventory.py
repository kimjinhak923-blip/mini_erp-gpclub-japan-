import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t, render_sidebar

st.set_page_config(page_title=t("nav_inventory"), page_icon="🏢", layout="wide")
require_auth()
render_sidebar()

st.title("🏢 창고별 재고 및 大吉商事 위탁 현황")

# 1. 大吉商事 위탁 평가액 (원가 KRW 기준)
daikichi = supabase.table("warehouses").select("id").eq("name", "大吉商事").execute().data
if daikichi:
    dk_id = daikichi[0]["id"]
    dk_inv = supabase.table("inventory") \
        .select("stock_qty, products(sku, name, purchase_cost_krw)") \
        .eq("warehouse_id", dk_id) \
        .gt("stock_qty", 0) \
        .execute().data or []
        
    tot_krw = 0
    dk_rows = []
    for row in dk_inv:
        p = row["products"]
        if not p:
            continue
        qty = row["stock_qty"]
        cost = float(p["purchase_cost_krw"] or 0)
        sum_krw = qty * cost
        tot_krw += sum_krw
        dk_rows.append({
            "SKU": p["sku"],
            "제품명": p["name"],
            "잔여 재고수량": qty,
            "매입단가(KRW)": f"₩{cost:,.0f}",
            "위탁 재고 평가액(KRW)": f"₩{sum_krw:,.0f}"
        })
        
    st.info("💡 **大吉商事 (위탁창고) 현황**")
    st.metric("大吉商事 총 위탁 재고 평가액 (원가 KRW 기준)", f"₩{tot_krw:,.0f}")
    if dk_rows:
        st.dataframe(pd.DataFrame(dk_rows), use_container_width=True)
    else:
        st.caption("大吉商事에 보관된 위탁 재고가 없습니다.")

st.markdown("---")

# 2. 월간 재고 변동 (도쿄 날짜 기준)
st.subheader("📦 전체 제품 월별 재고 흐름 (도쿄 날짜 기준)")

today = date.today()
first_day_this_month = date(today.year, today.month, 1)
last_day_prev_month = first_day_this_month - timedelta(days=1)

st.caption(f"기준월: **{today.month}월** (지난달: {last_day_prev_month.month}월 잔여 기준)")

prods = supabase.table("products").select("*").execute().data or []
summary_rows = []

for p in prods:
    out_res = supabase.table("sales_order_items") \
        .select("qty, sales_orders!inner(delivery_date)") \
        .eq("product_id", p["id"]) \
        .gte("sales_orders.delivery_date", first_day_this_month.isoformat()) \
        .execute().data or []
        
    this_month_out = sum(item["qty"] for item in out_res)
    
    inv_res = supabase.table("inventory").select("stock_qty").eq("product_id", p["id"]).execute().data or []
    current_stock = sum(i["stock_qty"] for i in inv_res)
    
    prev_stock = current_stock + this_month_out

    summary_rows.append({
        "SKU": p["sku"],
        "제품명": p["name"],
        f"지난달({last_day_prev_month.month}월) 잔여": prev_stock,
        "이번달 입고수량": 0,
        "이번달 출고수량": this_month_out,
        f"이번달({today.month}월) 잔여": current_stock
    })

st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)
