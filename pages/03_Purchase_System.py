import streamlit as st
import pandas as pd
from utils.db_client import supabase
from datetime import datetime

st.set_page_config(page_title="Purchase System", page_icon="🛒", layout="wide")
st.title("🛒 Purchase Management (구매/발주 & 입고 시스템)")
st.caption("공급처 발주 등록, 상태 관리 및 입고 완료 시 창고 재고 자동 반영")

tab1, tab2 = st.tabs(["➕ 신규 PO (구매 발주) 등록", "📋 발주 현황 및 입고/재고 반영"])

# 데이터 사전 로드 (Active 상태만)
suppliers_res = supabase.table("suppliers").select("id, supplier_code, name").eq("is_active", True).execute()
warehouses_res = supabase.table("warehouses").select("id, name").eq("is_active", True).execute()
products_res = supabase.table("products").select("id, sku, name, purchase_price").eq("is_active", True).execute()

suppliers = suppliers_res.data if suppliers_res.data else []
warehouses = warehouses_res.data if warehouses_res.data else []
products = products_res.data if products_res.data else []

supplier_dict = {f"[{s['supplier_code']}] {s['name']}": s['id'] for s in suppliers}
warehouse_dict = {w['name']: w['id'] for w in warehouses}
product_dict = {f"[{p['sku']}] {p['name']}": p for p in products}

# ==========================================
# 1. 신규 PO 등록
# ==========================================
with tab1:
    st.subheader("📝 구매 발주서(Purchase Order) 작성")
    
    if not suppliers or not warehouses or not products:
        st.warning("⚠️ Master Data(공급처, 창고, 상품)가 최소 1개 이상 등록되어 있어야 발주가 가능합니다.")
    else:
        with st.form("po_create_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            selected_supplier = col1.selectbox("공급처 선택*", list(supplier_dict.keys()))
            selected_warehouse = col2.selectbox("입고 예정 창고*", list(warehouse_dict.keys()))
            supplier_po_no = col3.text_input("공급처 발주번호 (선택)", placeholder="SUP-PO-2026-001")
            
            col4, col5 = st.columns(2)
            order_date = col4.date_input("발주일자", datetime.now())
            expected_date = col5.date_input("입고 예정일", datetime.now())
            
            st.divider()
            st.markdown("##### 📦 발주 품목 선택")
            
            col_p1, col_p2, col_p3 = st.columns([3, 2, 2])
            selected_prod_name = col_p1.selectbox("발주 상품*", list(product_dict.keys()))
            
            target_prod = product_dict[selected_prod_name]
            default_price = float(target_prod.get("purchase_price") or 0.0)
            
            quantity = col_p2.number_input("발주 수량*", min_value=1, value=10, step=1)
            unit_price = col_p3.number_input("단가 (KRW)*", min_value=0.0, value=default_price, step=1000.0)
            
            total_amount = quantity * unit_price
            st.info(f"💡 예상 총 발주 금액: **₩{total_amount:,.0f}**")
            
            notes = st.text_area("비고 (Notes)", placeholder="특이사항 입력")
            
            submitted = st.form_submit_button("🚀 발주서 생성 (REQUESTED)")
            
            if submitted:
                try:
                    supplier_id = supplier_dict[selected_supplier]
                    warehouse_id = warehouse_dict[selected_warehouse]
                    product_id = target_prod["id"]
                    
                    # 1) purchase_orders 헤더 등록
                    po_res = supabase.table("purchase_orders").insert({
                        "supplier_id": supplier_id,
                        "warehouse_id": warehouse_id,
                        "supplier_po_no": supplier_po_no,
                        "order_date": str(order_date),
                        "expected_delivery_date": str(expected_date),
                        "status": "REQUESTED",
                        "total_amount": total_amount,
                        "notes": notes
                    }).execute()
                    
                    new_po_id = po_res.data[0]["id"]
                    
                    # 2) po_items 상세 품목 등록
                    supabase.table("po_items").insert({
                        "po_id": new_po_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "subtotal": total_amount
                    }).execute()
                    
                    st.success(f"발주서가 성공적으로 생성되었습니다! (PO ID: {new_po_id[:8]}...)")
                    st.rerun()
                except Exception as e:
                    st.error(f"발주서 생성 실패: {e}")

# ==========================================
# 2. 발주 현황 및 입고 처리 (재고 자동 반영)
# ==========================================
with tab2:
    st.subheader("📋 발주 목록 조회 및 입고/재고 연동")
    
    status_filter = st.selectbox("상태 필터", ["ALL", "REQUESTED", "APPROVED", "RECEIVED", "CANCELLED"])
    
    query = supabase.table("purchase_orders").select(
        "*, suppliers(name), warehouses(name)"
    )
    if status_filter != "ALL":
        query = query.eq("status", status_filter)
        
    po_list_res = query.order("created_at", desc=True).execute()
    
    if po_list_res.data:
        for po in po_list_res.data:
            supplier_name = po.get("suppliers", {}).get("name") if po.get("suppliers") else "-"
            warehouse_name = po.get("warehouses", {}).get("name") if po.get("warehouses") else "-"
            status = po["status"]
            
            status_color = {
                "REQUESTED": "🟠",
                "APPROVED": "🔵",
                "RECEIVED": "🟢",
                "CANCELLED": "🔴"
            }.get(status, "⚪")
            
            with st.expander(f"{status_color} [{status}] 발주 ID: {po['id'][:8]}... | 공급처: {supplier_name} | 금액: ₩{po['total_amount']:,.0f}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**공급처:** {supplier_name}")
                c2.write(f"**입고 창고:** {warehouse_name}")
                c3.write(f"**상태:** {status}")
                
                c1.write(f"**발주일자:** {po['order_date']}")
                c2.write(f"**입고예정일:** {po['expected_delivery_date']}")
                c3.write(f"**공급처 PO 번호:** {po.get('supplier_po_no') or '-'}")
                
                # 발주 상세 항목 조회
                items_res = supabase.table("po_items").select("*, products(sku, name)").eq("po_id", po["id"]).execute()
                if items_res.data:
                    items_df = pd.DataFrame([{
                        "SKU": item.get("products", {}).get("sku"),
                        "상품명": item.get("products", {}).get("name"),
                        "수량": item["quantity"],
                        "단가": f"₩{item['unit_price']:,.0f}",
                        "소계": f"₩{item['subtotal']:,.0f}"
                    } for item in items_res.data])
                    st.dataframe(items_df, use_container_width=True)
                
                st.write(f"**비고:** {po.get('notes') or '없음'}")
                
                # 상태 변경 및 입고 처리 버튼
                col_b1, col_b2, col_b3 = st.columns(3)
                
                if status == "REQUESTED":
                    if col_b1.button("✅ 발주 승인 (APPROVE)", key=f"app_{po['id']}"):
                        supabase.table("purchase_orders").update({"status": "APPROVED"}).eq("id", po["id"]).execute()
                        st.success("발주가 승인되었습니다.")
                        st.rerun()
                        
                    if col_b2.button("❌ 발주 취소 (CANCEL)", key=f"can_{po['id']}"):
                        supabase.table("purchase_orders").update({"status": "CANCELLED"}).eq("id", po["id"]).execute()
                        st.warning("발주가 취소되었습니다.")
                        st.rerun()
                        
                elif status == "APPROVED":
                    if col_b1.button("📦 입고 완료 처리 (재고 자동 반영)", key=f"rec_{po['id']}"):
                        try:
                            # 1) po_items 내 품목별 재고(inventories) 자동 반영
                            for item in items_res.data:
                                p_id = item["product_id"]
                                w_id = po["warehouse_id"]
                                add_qty = item["quantity"]
                                
                                # 기존 재고 확인
                                inv_check = supabase.table("inventories").select("*").eq("product_id", p_id).eq("warehouse_id", w_id).execute()
                                
                                if inv_check.data:
                                    # 기존 재고 수량 증가
                                    cur_inv = inv_check.data[0]
                                    new_qty = cur_inv["quantity"] + add_qty
                                    supabase.table("inventories").update({"quantity": new_qty}).eq("id", cur_inv["id"]).execute()
                                else:
                                    # 신규 재고 데이터 생성
                                    supabase.table("inventories").insert({
                                        "product_id": p_id,
                                        "warehouse_id": w_id,
                                        "quantity": add_qty,
                                        "safety_stock": 10
                                    }).execute()
                            
                            # 2) PO 상태 RECEIVED 변경
                            supabase.table("purchase_orders").update({"status": "RECEIVED"}).eq("id", po["id"]).execute()
                            st.success("입고 처리가 완료되어 지정 창고의 재고가 자동 반영되었습니다!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"입고 처리 중 오류 발생: {e}")
    else:
        st.info("조회된 발주 내역이 없습니다.")
