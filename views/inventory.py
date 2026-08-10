import streamlit as st
import pandas as pd
from utils.supabase_client import supabase

def render():
    st.header("🏭 창고별 입출고 및 재고 현황")
    
    wh_res = supabase.table("warehouses").select("id, name, is_consignment").execute()
    wh_list = ["전체"] + [w["name"] for w in wh_res.data] if wh_res.data else ["전체"]
    
    selected_wh = st.selectbox("조회할 창고 선택", wh_list)
    
    # 재고 조회
    query = supabase.table("inventories").select("current_qty, warehouses(name, is_consignment), products(jan_code, sku, name, cost_krw)")
    if selected_wh != "전체":
        # 특정 창고 필터링
        query = query.eq("warehouses.name", selected_wh)
        
    res = query.execute()
    if res.data:
        rows = []
        for r in res.data:
            if not r.get("warehouses"): continue
            wh_name = r["warehouses"]["name"]
            is_consign = r["warehouses"]["is_consignment"]
            qty = r["current_qty"]
            cost_krw = float(r["products"]["cost_krw"] or 0) if r.get("products") else 0
            
            # 大吉商事(위탁)은 가격 반영 안 함
            total_krw = 0 if is_consign else (qty * cost_krw)
            
            rows.append({
                "창고명": wh_name + (" (위탁)" if is_consign else ""),
                "JAN": r["products"]["jan_code"] if r.get("products") else "-",
                "상품명": r["products"]["name"] if r.get("products") else "-",
                "재고 수량": qty,
                "매입 단가 (KRW)": f"₩ {cost_krw:,.0f}",
                "총 재고 평가금액": f"₩ {total_krw:,.0f}" if not is_consign else "₩ 0 (위탁 미반영)"
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
