import streamlit as st
import pandas as pd
from utils.supabase_client import supabase

def render():
    st.header("🛒 영업 및 출고(배송) 등록")
    tab1, tab2 = st.tabs(["출고/납품 등록 (배송 주소 입력)", "월별/거래처별 발주 현황"])
    
    with tab1:
        st.subheader("출고(Delivery) 등록")
        
        # 거래처 및 상품 정보
        cust_res = supabase.table("customers").select("id, name").execute()
        prod_res = supabase.table("products").select("id, name, jan_code").execute()
        wh_res = supabase.table("warehouses").select("id, name, is_consignment").execute()
        
        cust_map = {c["name"]: c["id"] for c in cust_res.data} if cust_res.data else {}
        prod_map = {f"[{p['jan_code']}] {p['name']}": p["id"] for p in prod_res.data} if prod_res.data else {}
        wh_map = {w["name"] + (" (위탁)" if w["is_consignment"] else ""): w["id"] for w in wh_res.data} if wh_res.data else {}

        col_c, col_p = st.columns(2)
        selected_cust = col_c.selectbox("1. 거래처 선택", list(cust_map.keys()))
        selected_prod = col_p.selectbox("2. 상품 선택", list(prod_map.keys()))
        
        # 선택한 거래처와 상품의 엔화 단가 자동 가져오기
        auto_jpy_price = 0.0
        if selected_cust and selected_prod:
            c_id = cust_map[selected_cust]
            p_id = prod_map[selected_prod]
            cp_res = supabase.table("customer_prices").select("price_jpy").eq("customer_id", c_id).eq("product_id", p_id).execute()
            if cp_res.data:
                auto_jpy_price = float(cp_res.data[0]["price_jpy"])

        with st.form("delivery_register_form"):
            st.write("📋 **출고 상세 정보 및 배송지 입력**")
            
            c1, c2, c3 = st.columns(3)
            qty = c1.number_input("출고 수량", min_value=1, step=1)
            unit_price = c2.number_input("적용 단가 (JPY)", value=auto_jpy_price)
            deliv_type = c3.selectbox("납품 구분", ["NORMAL (일반납품)", "FOC (무상)", "CONSIGNMENT (위탁)"])
            
            st.info(f"💡 자동 계산 총 금액: **¥ {qty * unit_price:,.2f} JPY**")
            
            st.write("🚛 **배송 주소지 정보**")
            a1, a2 = st.columns(2)
            deliv_name = a1.text_input("납품처명 (배송지 이름)")
            contact = a2.text_input("담당자명")
            
            a3, a4, a5 = st.columns(3)
            post_code = a3.text_input("우편번호")
            phone = a4.text_input("전화번호")
            sel_wh = a5.selectbox("출고 대상 창고", list(wh_map.keys()))
            
            address = st.text_input("상세 주소")
            
            if st.form_submit_button("출고(배송) 등록"):
                try:
                    # 1. 배송 헤더 등록
                    deliv_res = supabase.table("deliveries").insert({
                        "delivery_date": str(pd.Timestamp.now().date()),
                        "postal_code": post_code,
                        "address": address,
                        "contact_person": contact,
                        "delivery_location_name": deliv_name,
                        "phone_number": phone,
                        "delivery_type": deliv_type.split()[0],
                        "status": "COMPLETED"
                    }).execute()
                    
                    deliv_id = deliv_res.data[0]["id"]
                    
                    # 2. 배송 상세 item 등록
                    supabase.table("delivery_items").insert({
                        "delivery_id": deliv_id,
                        "product_id": prod_map[selected_prod],
                        "quantity": qty
                    }).execute()
                    
                    st.success("출고 등록이 정상 완료되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"출고 등록 실패: {e}")

    # Tab 2: 월별 / 거래처별 발주 및 출고 수량 집계
    with tab2:
        st.subheader("거래처별/월별 발주 및 출고 금액 조회")
        deliveries = supabase.table("deliveries").select("delivery_date, delivery_type, delivery_items(quantity, products(name)), postal_code, address, delivery_location_name").execute()
        if deliveries.data:
            st.dataframe(pd.DataFrame(deliveries.data), use_container_width=True)
