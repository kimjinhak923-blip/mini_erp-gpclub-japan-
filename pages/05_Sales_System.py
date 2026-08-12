import streamlit as st
import pandas as pd
from utils.db_client import supabase
from datetime import datetime

st.set_page_config(page_title="Sales System", page_icon="🏢", layout="wide")
st.title("🏢 Sales Management (B2B 영업 & 출고/납품 시스템)")
st.caption("Sales Order (SO) 작성, 납품/배송 등록 및 출고 완료 시 창고 재고 자동 차감")

tab1, tab2, tab3 = st.tabs(["📝 신규 B2B 주문 (SO) 등록", "🚚 납품/배송 (Delivery) 및 출고 자동 차감", "📋 영업/납품 현황 조회"])

# 마스터 데이터 로드 (Active 상태만)
customers_res = supabase.table("customers").select("id, customer_code, name, currency").eq("is_active", True).execute()
warehouses_res = supabase.table("warehouses").select("id, name").eq("is_active", True).execute()
products_res = supabase.table("products").select("id, sku, name, selling_price").eq("is_active", True).execute()

customers = customers_res.data if customers_res.data else []
warehouses = warehouses_res.data if warehouses_res.data else []
products = products_res.data if products_res.data else []

customer_dict = {f"[{c['customer_code']}] {c['name']} ({c['currency']})": c for c in customers}
warehouse_dict = {w['name']: w['id'] for w in warehouses}
product_dict = {f"[{p['sku']}] {p['name']}": p for p in products}

# ==========================================
# 1. 신규 B2B Sales Order (SO) 등록
# ==========================================
with tab1:
    st.subheader("📝 B2B 수주(Sales Order) 작성")
    
    if not customers or not products:
        st.warning("⚠️ Master Data(거래처, 상품)가 최소 1개 이상 등록되어 있어야 주문 작성이 가능합니다.")
    else:
        with st.form("so_create_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            selected_cust_label = col1.selectbox("거래처(Customer) 선택*", list(customer_dict.keys()))
            order_date = col2.date_input("주문일자", datetime.now())
            
            st.divider()
            st.markdown("##### 📦 주문 품목 선택")
            
            col_p1, col_p2, col_p3 = st.columns([3, 2, 2])
            selected_prod_label = col_p1.selectbox("주문 상품*", list(product_dict.keys()))
            
            target_prod = product_dict[selected_prod_label]
            default_price = float(target_prod.get("selling_price") or 0.0)
            
            quantity = col_p2.number_input("주문 수량*", min_value=1, value=10, step=1)
            unit_price = col_p3.number_input("판매 단가 (KRW)*", min_value=0.0, value=default_price, step=1000.0)
            
            total_amount = quantity * unit_price
            st.info(f"💡 총 수주 금액: **₩{total_amount:,.0f}**")
            
            submitted_so = st.form_submit_button("🚀 Sales Order 등록 (CONFIRMED)")
            
            if submitted_so:
                try:
                    cust_info = customer_dict[selected_cust_label]
                    
                    # 1) sales_orders 헤더 저장
                    so_res = supabase.table("sales_orders").insert({
                        "customer_id": cust_info["id"],
                        "order_date": str(order_date),
                        "status": "CONFIRMED",
                        "total_amount": total_amount
                    }).execute()
                    
                    new_so_id = so_res.data[0]["id"]
                    
                    # 2) so_items 상세 저장
                    supabase.table("so_items").insert({
                        "so_id": new_so_id,
                        "product_id": target_prod["id"],
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "subtotal": total_amount
                    }).execute()
                    
                    st.success(f"Sales Order가 성공적으로 등록되었습니다! (SO ID: {new_so_id[:8]}...)")
                    st.rerun()
                except Exception as e:
                    st.error(f"주문 등록 실패: {e}")


# ==========================================
# 2. Delivery (납품) 등록 및 출고 자동 차감
# ==========================================
with tab2:
    st.subheader("🚚 납품/배송 등록 및 출고(재고 차감) 처리")
    st.caption("배송 상태를 'COMPLETED'로 완료 처리하면 선택한 창고의 재고가 자동으로 차감됩니다.")
    
    # CONFIRMED 상태인 SO 목록 가져오기
    so_list_res = supabase.table("sales_orders").select(
        "*, customers(name)"
    ).filter("status", "in", "('CONFIRMED', 'PARTIAL')").order("created_at", desc=True).execute()
    
    if not so_list_res.data or not warehouses:
        st.info("현재 납품 처리 대기 중인 주문이 없거나 출고 창고 정보가 없습니다.")
    else:
        so_options = {f"SO-ID: {so['id'][:8]}... | 거래처: {so.get('customers', {}).get('name', '-')} | 금액: ₩{so['total_amount']:,.0f}": so for so in so_list_res.data}
        
        with st.form("delivery_create_form", clear_on_submit=True):
            selected_so_label = st.selectbox("납품 대상 Sales Order 선택*", list(so_options.keys()))
            target_so = so_options[selected_so_label]
            
            col_d1, col_d2 = st.columns(2)
            out_warehouse_label = col_d1.selectbox("출고 창고 선택*", list(warehouse_dict.keys()))
            delivery_no = col_d2.text_input("송장/운송장 번호 (Delivery No)", placeholder="DELIV-2026-001")
            
            col_d3, col_d4 = st.columns(2)
            delivery_date = col_d3.date_input("출고/배송 일자", datetime.now())
            shipping_fee = col_d4.number_input("배송비 (KRW)", min_value=0.0, value=3000.0, step=500.0)
            
            st.warning("⚠️ '출고 확정 및 재고 차감' 버튼을 누르면 즉시 해당 창고의 재고가 차감되고 Deliveries 상태가 COMPLETED로 등록됩니다.")
            submitted_deliv = st.form_submit_button("📦 출고 확정 및 재고 자동 차감")
            
            if submitted_deliv:
                target_wh_id = warehouse_dict[out_warehouse_label]
                so_id = target_so["id"]
                
                try:
                    # 1) SO Item 항목들 확인
                    so_items_res = supabase.table("so_items").select("*").eq("so_id", so_id).execute()
                    so_items = so_items_res.data if so_items_res.data else []
                    
                    # 2) 재고 수량 충분 여부 사전 검증
                    stock_insufficient = False
                    for item in so_items:
                        p_id = item["product_id"]
                        req_qty = item["quantity"]
                        
                        inv_res = supabase.table("inventories").select("*").eq("warehouse_id", target_wh_id).eq("product_id", p_id).execute()
                        curr_qty = inv_res.data[0]["quantity"] if inv_res.data else 0
                        
                        if curr_qty < req_qty:
                            st.error(f"❌ 선택한 창고({out_warehouse_label})의 재고가 부족합니다. (현재 재고: {curr_qty}개 / 필요 수량: {req_qty}개)")
                            stock_insufficient = True
                            break
                            
                    if not stock_insufficient:
                        # 3) 재고 차감 수행
                        for item in so_items:
                            p_id = item["product_id"]
                            req_qty = item["quantity"]
                            
                            inv_res = supabase.table("inventories").select("*").eq("warehouse_id", target_wh_id).eq("product_id", p_id).execute()
                            inv_record = inv_res.data[0]
                            new_qty = inv_record["quantity"] - req_qty
                            
                            supabase.table("inventories").update({"quantity": new_qty}).eq("id", inv_record["id"]).execute()
                            
                        # 4) Deliveries 레코드 생성
                        deliv_res = supabase.table("deliveries").insert({
                            "so_id": so_id,
                            "delivery_no": delivery_no or f"DEL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "delivery_date": str(delivery_date),
                            "status": "COMPLETED",
                            "deal_type": "B2B",
                            "shipping_fee": shipping_fee
                        }).execute()
                        
                        # 5) SO 상태 FULFILLED 업데이트
                        supabase.table("sales_orders").update({"status": "FULFILLED"}).eq("id", so_id).execute()
                        
                        st.success("✅ 출고 처리 및 재고 차감이 성공적으로 진행되었습니다!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"출고 처리 오류: {e}")


# ==========================================
# 3. 영업/납품 현황 조회
# ==========================================
with tab3:
    st.subheader("📋 영업 및 납품 트랜잭션 현황")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("##### 🛒 Sales Orders (주문 내역)")
        so_data = supabase.table("sales_orders").select("*, customers(name)").order("created_at", desc=True).execute()
        if so_data.data:
            df_so = pd.DataFrame([{
                "SO ID": item["id"][:8] + "...",
                "거래처": item.get("customers", {}).get("name", "-"),
                "주문일": item["order_date"],
                "상태": item["status"],
                "총 금액": f"₩{item['total_amount']:,.0f}"
            } for item in so_data.data])
            st.dataframe(df_so, use_container_width=True)
        else:
            st.info("등록된 주문 내역이 없습니다.")
            
    with col_t2:
        st.markdown("##### 🚚 Deliveries (납품/배송 내역)")
        deliv_data = supabase.table("deliveries").select("*").order("created_at", desc=True).execute()
        if deliv_data.data:
            df_deliv = pd.DataFrame([{
                "배송 ID": item["id"][:8] + "...",
                "송장번호": item.get("delivery_no", "-"),
                "배송일자": item["delivery_date"],
                "유형": item.get("deal_type", "B2B"),
                "상태": item["status"],
                "배송비": f"₩{item['shipping_fee']:,.0f}"
            } for item in deliv_data.data])
            st.dataframe(df_deliv, use_container_width=True)
        else:
            st.info("등록된 납품/배송 내역이 없습니다.")
