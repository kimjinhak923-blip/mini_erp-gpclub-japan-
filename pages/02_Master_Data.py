import streamlit as st
import pandas as pd
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t, render_sidebar

st.set_page_config(page_title=t("nav_master"), page_icon="⚙️", layout="wide")
require_auth()
render_sidebar()

st.title("⚙️ 마스터 정보 관리")

tab_prod, tab_partner, tab_mapping, tab_stock = st.tabs(["📦 제품 마스터", "🏢 거래처 마스터", "🔗 거래처별 제품/공급가", "📥 창고별 초기 재고 등록"])

# 1. 제품 마스터
with tab_prod:
    with st.form("add_product_form"):
        st.subheader("새 제품 등록")
        c1, c2, c3, c4, c5 = st.columns(5)
        sku = c1.text_input("SKU 코드")
        p_name = c2.text_input("제품명")
        cost_krw = c3.number_input("매입단가(원가 KRW)", min_value=0.0)
        price_jpy = c4.number_input("기본 공급가(JPY, Vat-)", min_value=0.0)
        box_qty = c5.number_input("Box당 입수량", min_value=1, value=1)
        
        if st.form_submit_button("제품 추가") and sku and p_name:
            supabase.table("products").insert({
                "sku": sku, "name": p_name, "purchase_cost_krw": cost_krw, 
                "supply_price_jpy": price_jpy, "items_per_box": box_qty
            }).execute()
            st.success("제품이 등록되었습니다.")
            st.rerun()

    prods = supabase.table("products").select("*").execute().data or []
    st.dataframe(pd.DataFrame(prods), use_container_width=True)

# 2. 거래처 마스터
with tab_partner:
    with st.form("add_partner_form"):
        st.subheader("새 거래처 등록")
        c1, c2, c3, c4 = st.columns(4)
        code = c1.text_input("거래처 코드")
        name = c2.text_input("거래처명")
        phone = c3.text_input("전화번호")
        addr = c4.text_input("주소")
        if st.form_submit_button("거래처 추가") and code and name:
            supabase.table("partners").insert({"code": code, "name": name, "phone": phone, "address": addr}).execute()
            st.success("거래처가 등록되었습니다.")
            st.rerun()

    partners = supabase.table("partners").select("*").execute().data or []
    st.dataframe(pd.DataFrame(partners), use_container_width=True)

# 3. 거래처별 지정 제품 & 전용 공급가
with tab_mapping:
    st.subheader("거래처별 거래 가능 제품 및 전용 공급가 설정")
    if partners and prods:
        partner_map = {p["name"]: p["id"] for p in partners}
        prod_map = {f"[{p['sku']}] {p['name']}": p for p in prods}
        
        sel_partner = st.selectbox("거래처 선택", list(partner_map.keys()), key="m_map_partner")
        sel_prod_label = st.selectbox("거래 가능 제품 선택", list(prod_map.keys()), key="m_map_prod")
        
        target_prod = prod_map[sel_prod_label]
        custom_price = st.number_input("거래처 전용 공급가 (JPY, VAT별도)", value=float(target_prod["supply_price_jpy"]), key="m_map_price")
        
        if st.button("거래처 제품 지정 등록"):
            supabase.table("partner_products").upsert({
                "partner_id": partner_map[sel_partner],
                "product_id": target_prod["id"],
                "custom_supply_price_jpy": custom_price
            }).execute()
            st.success("거래처별 제품 지정이 완료되었습니다.")

# 4. 창고별 초기 재고 조정/입고
with tab_stock:
    st.subheader("창고별 제품 재고 수량 등록/조정")
    warehouses = supabase.table("warehouses").select("*").execute().data or []
    if warehouses and prods:
        wh_map = {w["name"]: w["id"] for w in warehouses}
        prod_map2 = {f"[{p['sku']}] {p['name']}": p["id"] for p in prods}
        
        c_wh, c_p, c_q = st.columns(3)
        sel_wh = c_wh.selectbox("창고 선택", list(wh_map.keys()), key="m_stk_wh")
        sel_p = c_p.selectbox("제품 선택", list(prod_map2.keys()), key="m_stk_prod")
        stk_qty = c_q.number_input("재고 수량", min_value=0, value=100, key="m_stk_qty")
        
        if st.button("재고 수량 저장"):
            supabase.table("inventory").upsert({
                "warehouse_id": wh_map[sel_wh],
                "product_id": prod_map2[sel_p],
                "stock_qty": stk_qty
            }).execute()
            st.success("창고별 재고가 업데이트되었습니다.")
