import streamlit as st
import pandas as pd
from utils.db_client import supabase

st.set_page_config(page_title="Inventory System", page_icon="📦", layout="wide")
st.title("📦 Inventory Management (재고 통합 관리 시스템)")
st.caption("창고별 재고 실시간 조회, 안전재고 부족 알림, 창고 간 재고 이동 및 조정")

tab1, tab2, tab3 = st.tabs(["📊 실시간 재고 현황 & 안전재고 알림", "🚚 창고 간 재고 이동 (Transfer)", "🔧 재고 수동 조정 (Adjustment)"])

# 마스터 데이터 로드
warehouses_res = supabase.table("warehouses").select("id, name").eq("is_active", True).execute()
products_res = supabase.table("products").select("id, sku, name, purchase_price").eq("is_active", True).execute()

warehouses = warehouses_res.data if warehouses_res.data else []
products = products_res.data if products_res.data else []

warehouse_dict = {w['name']: w['id'] for w in warehouses}
product_dict = {f"[{p['sku']}] {p['name']}": p for p in products}

# ==========================================
# 1. 실시간 재고 현황 & 안전재고 알림
# ==========================================
with tab1:
    st.subheader("📊 창고별 재고 현황")
    
    col_w, col_alert = st.columns([2, 2])
    selected_wh_filter = col_w.selectbox("창고 필터", ["전체 창고"] + list(warehouse_dict.keys()))
    only_low_stock = col_alert.checkbox("⚠️ 안전재고 미달(부족) 품목만 보기")
    
    # inventories 데이터 조회
    query = supabase.table("inventories").select("*, products(sku, name, category, purchase_price), warehouses(name)")
    
    if selected_wh_filter != "전체 창고":
        query = query.eq("warehouse_id", warehouse_dict[selected_wh_filter])
        
    inv_res = query.execute()
    
    if inv_res.data:
        processed_data = []
        low_stock_count = 0
        total_qty = 0
        total_value = 0.0
        
        for inv in inv_res.data:
            p_info = inv.get("products") or {}
            w_info = inv.get("warehouses") or {}
            
            qty = inv.get("quantity", 0)
            safety = inv.get("safety_stock", 0)
            p_price = float(p_info.get("purchase_price") or 0.0)
            asset_val = qty * p_price
            
            is_low = qty <= safety
            if is_low:
                low_stock_count += 1
                
            if only_low_stock and not is_low:
                continue
                
            total_qty += qty
            total_value += asset_val
            
            processed_data.append({
                "창고명": w_info.get("name", "-"),
                "SKU": p_info.get("sku", "-"),
                "상품명": p_info.get("name", "-"),
                "카테고리": p_info.get("category", "-"),
                "현재 재고": qty,
                "안전 재고": safety,
                "재고 상태": "⚠️ 경고 (부족)" if is_low else "🟢 정상",
                "평균 매입가": f"₩{p_price:,.0f}",
                "총 재고 자산": f"₩{asset_val:,.0f}"
            })
            
        # Summary KPI Cards
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("총 재고 수량", f"{total_qty:,} 개")
        kpi2.metric("안전재고 미달 품목 수", f"{low_stock_count} 건", delta="-부족" if low_stock_count > 0 else "정상", delta_color="inverse")
        kpi3.metric("총 재고 자산 가치", f"₩{total_value:,.0f}")
        
        st.divider()
        
        if processed_data:
            df_inv = pd.DataFrame(processed_data)
            st.dataframe(df_inv, use_container_width=True)
        else:
            st.info("조건에 맞는 재고 데이터가 없습니다.")
    else:
        st.info("등록된 재고 데이터가 없습니다. 구매/발주(PO) 입고 완료 시 자동으로 생성됩니다.")


# ==========================================
# 2. 창고 간 재고 이동 (Transfer)
# ==========================================
with tab2:
    st.subheader("🚚 창고 간 재고 이동 (Stock Transfer)")
    st.caption("출발 창고의 재고를 차감하고, 도착 창고의 재고를 자동으로 증가시킵니다.")
    
    if len(warehouses) < 2:
        st.warning("⚠️ 재고 이동을 하려면 창고가 최소 2개 이상 등록되어 있어야 합니다.")
    else:
        with st.form("transfer_form", clear_on_submit=True):
            col_from, col_to = st.columns(2)
            from_wh = col_from.selectbox("출발 창고 (Source)*", list(warehouse_dict.keys()), key="from_wh")
            
            # 도착 창고 옵션에서 출발 창고 제외
            to_wh_options = [w for w in warehouse_dict.keys() if w != from_wh]
            to_wh = col_to.selectbox("도착 창고 (Destination)*", to_wh_options, key="to_wh")
            
            col_p, col_q = st.columns([3, 1])
            selected_prod_label = col_p.selectbox("이동 대상 상품*", list(product_dict.keys()))
            transfer_qty = col_q.number_input("이동 수량*", min_value=1, value=1, step=1)
            
            submitted_transfer = st.form_submit_button("🚀 재고 이동 실행")
            
            if submitted_transfer:
                from_wh_id = warehouse_dict[from_wh]
                to_wh_id = warehouse_dict[to_wh]
                prod_id = product_dict[selected_prod_label]["id"]
                
                try:
                    # 1) 출발 창고 재고 확인
                    from_inv = supabase.table("inventories").select("*").eq("warehouse_id", from_wh_id).eq("product_id", prod_id).execute()
                    
                    if not from_inv.data or from_inv.data[0]["quantity"] < transfer_qty:
                        current_avail = from_inv.data[0]["quantity"] if from_inv.data else 0
                        st.error(f"출발 창고의 재고가 부족합니다. (현재 재고: {current_avail}개 / 요청 수량: {transfer_qty}개)")
                    else:
                        # 2) 출발 창고 차감
                        from_record = from_inv.data[0]
                        new_from_qty = from_record["quantity"] - transfer_qty
                        supabase.table("inventories").update({"quantity": new_from_qty}).eq("id", from_record["id"]).execute()
                        
                        # 3) 도착 창고 증가 (기존 존재 여부 체크)
                        to_inv = supabase.table("inventories").select("*").eq("warehouse_id", to_wh_id).eq("product_id", prod_id).execute()
                        
                        if to_inv.data:
                            to_record = to_inv.data[0]
                            new_to_qty = to_record["quantity"] + transfer_qty
                            supabase.table("inventories").update({"quantity": new_to_qty}).eq("id", to_record["id"]).execute()
                        else:
                            supabase.table("inventories").insert({
                                "warehouse_id": to_wh_id,
                                "product_id": prod_id,
                                "quantity": transfer_qty,
                                "safety_stock": 10
                            }).execute()
                            
                        st.success(f"성공적으로 {from_wh} $\\rightarrow$ {to_wh} 로 {product_dict[selected_prod_label]['name']} {transfer_qty}개가 이동되었습니다.")
                        st.rerun()
                except Exception as e:
                    st.error(f"재고 이동 실패: {e}")


# ==========================================
# 3. 재고 수동 조정 (Adjustment)
# ==========================================
with tab3:
    st.subheader("🔧 재고 실사 및 수동 수량 조정 (Inventory Adjustment)")
    st.caption("실제 재고 조사(실사) 결과에 따라 재고 수량 및 안전재고를 직접 수정합니다.")
    
    with st.form("adj_form", clear_on_submit=True):
        col_a1, col_a2 = st.columns(2)
        adj_wh = col_a1.selectbox("대상 창고*", list(warehouse_dict.keys()), key="adj_wh")
        adj_prod = col_a2.selectbox("대상 상품*", list(product_dict.keys()), key="adj_prod")
        
        col_q1, col_q2 = st.columns(2)
        new_quantity = col_q1.number_input("변경할 재고 수량*", min_value=0, value=0, step=1)
        new_safety = col_q2.number_input("변경할 안전재고 수량*", min_value=0, value=10, step=1)
        
        submitted_adj = st.form_submit_button("💾 재고 수치 반영")
        
        if submitted_adj:
            wh_id = warehouse_dict[adj_wh]
            p_id = product_dict[adj_prod]["id"]
            
            try:
                exist_inv = supabase.table("inventories").select("*").eq("warehouse_id", wh_id).eq("product_id", p_id).execute()
                
                if exist_inv.data:
                    supabase.table("inventories").update({
                        "quantity": new_quantity,
                        "safety_stock": new_safety
                    }).eq("id", exist_inv.data[0]["id"]).execute()
                else:
                    supabase.table("inventories").insert({
                        "warehouse_id": wh_id,
                        "product_id": p_id,
                        "quantity": new_quantity,
                        "safety_stock": new_safety
                    }).execute()
                    
                st.success("재고 수량이 성공적으로 조정되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"재고 조정 실패: {e}")
