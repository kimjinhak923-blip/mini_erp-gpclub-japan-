import streamlit as st
import pandas as pd
from utils.supabase_client import supabase

def render():
    st.header("📦 마스터 데이터 관리")
    tab1, tab2, tab3 = st.tabs(["상품 규격 마스터", "거래처별 엔화 공급가", "거래처 관리"])
    
    # Tab 1: 제품 상세 마스터 (JAN, 규격, 매입가 원화)
    with tab1:
        st.subheader("제품 마스터 등록")
        with st.expander("➕ 신규 제품(SKU) 등록"):
            with st.form("add_product_detail_form"):
                c1, c2, c3 = st.columns(3)
                jan_code = c1.text_input("JAN 코드")
                sku = c2.text_input("SKU 코드")
                name = c3.text_input("상품명")
                
                c4, c5, c6 = st.columns(3)
                volume = c4.text_input("상품 용량 (예: 500ml)")
                cost_krw = c5.number_input("매입가 (원화 KRW)", min_value=0.0, step=100.0)
                box_inner_qty = c6.number_input("박스 입수량 (곽/낱장)", min_value=0, step=1)
                
                c7, c8 = st.columns(2)
                inner_box_size = c7.text_input("곽 사이즈 (가로*세로*높이 mm)")
                outer_box_size = c8.text_input("박스 사이즈 (가로*세로*높이 mm)")
                
                c9, c10 = st.columns(2)
                plt_inner_qty = c9.number_input("1 PLT 곽 수량", min_value=0, step=1)
                plt_box_qty = c10.number_input("1 PLT 박스 수량", min_value=0, step=1)
                
                if st.form_submit_button("상품 저장"):
                    try:
                        supabase.table("products").insert({
                            "jan_code": jan_code, "sku": sku, "name": name,
                            "volume": volume, "cost_krw": cost_krw, "box_inner_qty": box_inner_qty,
                            "inner_box_size": inner_box_size, "outer_box_size": outer_box_size,
                            "plt_inner_qty": plt_inner_qty, "plt_box_qty": plt_box_qty
                        }).execute()
                        st.success("상품 마스터 등록 완료")
                        st.rerun()
                    except Exception as e:
                        st.error(f"등록 오류: {e}")

        # 상품 목록 표출
        prods = supabase.table("products").select("*").execute()
        if prods.data:
            st.dataframe(pd.DataFrame(prods.data), use_container_width=True)

    # Tab 2: 거래처별 엔화 공급가 관리
    with tab2:
        st.subheader("거래처별 엔화(JPY) 공급가 설정")
        cust_res = supabase.table("customers").select("id, name").execute()
        prod_res = supabase.table("products").select("id, name, jan_code").execute()
        
        cust_dict = {c["name"]: c["id"] for c in cust_res.data} if cust_res.data else {}
        prod_dict = {f"[{p['jan_code']}] {p['name']}": p["id"] for p in prod_res.data} if prod_res.data else {}

        with st.form("set_cust_price_form"):
            c1, c2, c3 = st.columns(3)
            sel_cust = c1.selectbox("거래처 선택", list(cust_dict.keys()))
            sel_prod = c2.selectbox("상품 선택", list(prod_dict.keys()))
            price_jpy = c3.number_input("공급 단가 (엔화 JPY)", min_value=0.0, step=10.0)
            
            if st.form_submit_button("공급가 저장"):
                try:
                    supabase.table("customer_prices").upsert({
                        "customer_id": cust_dict[sel_cust],
                        "product_id": prod_dict[sel_prod],
                        "price_jpy": price_jpy
                    }, on_conflict="customer_id, product_id").execute()
                    st.success("거래처별 엔화 단가 세팅 완료!")
                except Exception as e:
                    st.error(f"저장 오류: {e}")

        # 공급가 매핑 리스트
        prices = supabase.table("customer_prices").select("price_jpy, customers(name), products(name, jan_code)").execute()
        if prices.data:
            p_rows = []
            for p in prices.data:
                p_rows.append({
                    "거래처명": p["customers"]["name"] if p.get("customers") else "-",
                    "JAN 코드": p["products"]["jan_code"] if p.get("products") else "-",
                    "상품명": p["products"]["name"] if p.get("products") else "-",
                    "지정 공급가 (JPY)": f"¥ {p['price_jpy']:,.2f}"
                })
            st.dataframe(pd.DataFrame(p_rows), use_container_width=True)

    # Tab 3: 거래처 관리
    with tab3:
        st.subheader("거래처 목록")
        custs = supabase.table("customers").select("*").execute()
        if custs.data:
            st.dataframe(pd.DataFrame(custs.data), use_container_width=True)
