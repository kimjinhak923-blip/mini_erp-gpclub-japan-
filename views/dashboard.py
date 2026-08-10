import streamlit as st
import pandas as pd
from utils.supabase_client import supabase

def render():
    st.header("📊 경영 & 재고 종합 대시보드")
    
    # 1. 핵심 KPI 카드 (원화 자산 평가액 등)
    try:
        inv_res = supabase.table("inventories").select(
            "current_qty, warehouses(name, is_consignment), products(cost_krw)"
        ).execute()
        
        total_krw_val = 0
        total_stock_qty = 0
        consignment_qty = 0
        
        if inv_res.data:
            for item in inv_res.data:
                qty = item.get("current_qty", 0)
                is_consign = item["warehouses"]["is_consignment"] if item.get("warehouses") else False
                cost_krw = item["products"]["cost_krw"] if item.get("products") else 0
                
                total_stock_qty += qty
                if is_consign:
                    consignment_qty += qty
                else:
                    # 위탁창고(大吉商事)가 아닌 일반 창고만 재고 평가액 산출
                    total_krw_val += (qty * cost_krw)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 보유 재고 수량", f"{total_stock_qty:,} 개")
        col2.metric("총 자산 재고 평가액 (KRW)", f"₩ {total_krw_val:,.0f}")
        col3.metric("위탁 재고 수량 (大吉商事)", f"{consignment_qty:,} 개")
        col4.metric("운영 창고 수", "3 개 (SAGAWA / L&K / 大吉)")

    except Exception as e:
        st.error(f"KPI 지표 조회 실패: {e}")

    st.markdown("---")
    
    # 2. 창고별 품목 잔여 재고 및 평가금액 현황표
    st.subheader("🏢 창고별 품목 잔여 재고 및 자산 금액 (KRW)")
    try:
        raw_inv = supabase.table("inventories").select(
            "current_qty, allocated_qty, warehouses(name, is_consignment), products(jan_code, sku, name, cost_krw)"
        ).execute()
        
        if raw_inv.data:
            rows = []
            for r in raw_inv.data:
                wh_name = r["warehouses"]["name"] if r.get("warehouses") else "-"
                is_consign = r["warehouses"]["is_consignment"] if r.get("warehouses") else False
                cost_krw = float(r["products"]["cost_krw"] or 0) if r.get("products") else 0.0
                qty = r["current_qty"]
                
                # 위탁창고인 경우 평가금액은 0원 처리
                eval_amount_krw = 0.0 if is_consign else (qty * cost_krw)
                
                rows.append({
                    "창고 구분": wh_name + (" (위탁)" if is_consign else ""),
                    "JAN 코드": r["products"]["jan_code"] if r.get("products") else "-",
                    "SKU": r["products"]["sku"] if r.get("products") else "-",
                    "상품명": r["products"]["name"] if r.get("products") else "-",
                    "매입단가 (KRW)": f"₩ {cost_krw:,.0f}",
                    "현재 재고": f"{qty:,}",
                    "잔여 재고 원화 평가금액": f"₩ {eval_amount_krw:,.0f}" if not is_consign else "₩ 0 (위탁계정)"
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
    except Exception as e:
        st.error(f"창고별 현황 조회 오류: {e}")
