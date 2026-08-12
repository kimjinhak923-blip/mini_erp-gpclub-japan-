import streamlit as st
from datetime import date
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t, render_sidebar

st.set_page_config(page_title=t("order_title"), page_icon="📦", layout="wide")
require_auth()
render_sidebar()

st.title(t("order_title"))

partners = supabase.table("partners").select("*").execute().data or []
warehouses = supabase.table("warehouses").select("*").execute().data or []

if not partners or not warehouses:
    st.warning("거래처 및 창고 마스터를 먼저 등록해 주세요.")
    st.stop()

col_h1, col_h2, col_h3 = st.columns(3)
order_no = col_h1.text_input(t("order_no"), value=f"SO-{date.today().strftime('%Y%m%d')}-01")
partner_dict = {p["name"]: p for p in partners}
selected_partner_name = col_h2.selectbox(t("partner_select"), list(partner_dict.keys()), key="so_partner")
selected_partner = partner_dict[selected_partner_name]

wh_dict = {w["name"]: w["id"] for w in warehouses}
selected_wh_name = col_h3.selectbox(t("wh_select"), list(wh_dict.keys()), key="so_wh")
selected_wh_id = wh_dict[selected_wh_name]

st.subheader(t("delivery_dest"))
col_d1, col_d2, col_d3, col_d4 = st.columns(4)
deliv_name = col_d1.text_input(t("deliv_name"), value=selected_partner["name"])
zipcode = col_d2.text_input(t("deliv_zip"))
address = col_d3.text_input(t("deliv_addr"), value=selected_partner.get("address") or "")
phone = col_d4.text_input(t("deliv_phone"), value=selected_partner.get("phone") or "")

col_dt1, col_dt2 = st.columns(2)
order_date = col_dt1.date_input(t("order_date"), value=date.today())
delivery_date = col_dt2.date_input(t("delivery_date"), value=date.today())

st.markdown("---")
st.subheader(t("item_list"))
st.caption(t("no_stock_warn"))

partner_prods = supabase.table("partner_products") \
    .select("custom_supply_price_jpy, products(*)") \
    .eq("partner_id", selected_partner["id"]) \
    .execute().data or []

available_items = []
for pp in partner_prods:
    p = pp["products"]
    if not p:
        continue
    inv = supabase.table("inventory") \
        .select("stock_qty") \
        .eq("warehouse_id", selected_wh_id) \
        .eq("product_id", p["id"]) \
        .execute().data
    
    stock = inv[0]["stock_qty"] if inv else 0
    if stock > 0:
        available_items.append({
            "product_id": p["id"],
            "name": p["name"],
            "sku": p["sku"],
            "price": pp["custom_supply_price_jpy"],
            "items_per_box": p["items_per_box"],
            "stock": stock
        })

item_options = {f"[{i['sku']}] {i['name']} (재고:{i['stock']})": i for i in available_items}

if "order_rows" not in st.session_state:
    st.session_state["order_rows"] = 1

col_btn1, col_btn2, _ = st.columns([1, 1, 4])
if col_btn1.button("➕ 품목 추가") and st.session_state["order_rows"] < 30:
    st.session_state["order_rows"] += 1
if col_btn2.button("➖ 품목 삭제") and st.session_state["order_rows"] > 1:
    st.session_state["order_rows"] -= 1

grand_total_qty = 0
grand_total_amount = 0.0
items_to_save = []

if not item_options:
    st.error("⚠️ 선택한 창고에 거래처 지정 등록 제품의 보유 재고(>0)가 없습니다.")
else:
    for idx in range(st.session_state["order_rows"]):
        c_p, c_pr, c_q, c_bx, c_tot = st.columns([3, 1.5, 1.5, 1.5, 2])
        sel_p = c_p.selectbox(f"제품 #{idx+1}", list(item_options.keys()), key=f"so_p_{idx}")
        p_obj = item_options[sel_p]
        
        unit_p = c_pr.number_input(t("unit_price"), value=float(p_obj["price"]), disabled=True, key=f"so_pr_{idx}")
        qty = c_q.number_input(t("qty"), min_value=0, max_value=p_obj["stock"], value=0, key=f"so_q_{idx}")
        
        box_count = round(qty / p_obj["items_per_box"], 2) if p_obj["items_per_box"] else qty
        c_bx.number_input(t("box_qty"), value=box_count, disabled=True, key=f"so_bx_{idx}")
        
        row_tot = unit_p * qty
        c_tot.number_input(t("total_amount"), value=row_tot, disabled=True, key=f"so_tot_{idx}")
        
        if qty > 0:
            grand_total_qty += qty
            grand_total_amount += row_tot
            items_to_save.append({
                "product_id": p_obj["product_id"],
                "unit_price_jpy": unit_p,
                "qty": qty,
                "box_qty": box_count,
                "total_price_jpy": row_tot
            })

    st.markdown("---")
    m_col1, m_col2 = st.columns(2)
    m_col1.metric(t("grand_total_qty"), f"{grand_total_qty:,} 개")
    m_col2.metric(t("grand_total_amount"), f"¥{grand_total_amount:,.0f}")

    if st.button(t("submit_order"), type="primary", use_container_width=True):
        if grand_total_qty == 0:
            st.error("발주 수량을 최소 1개 이상 입력해 주세요.")
        else:
            order_res = supabase.table("sales_orders").insert({
                "order_no": order_no,
                "partner_id": selected_partner["id"],
                "delivery_name": deliv_name,
                "zipcode": zipcode,
                "address": address,
                "phone": phone,
                "order_date": order_date.isoformat(),
                "delivery_date": delivery_date.isoformat(),
                "warehouse_id": selected_wh_id,
                "total_qty": grand_total_qty,
                "total_amount_jpy": grand_total_amount
            }).execute()
            
            new_order_id = order_res.data[0]["id"]
            
            for item in items_to_save:
                item["order_id"] = new_order_id
                supabase.table("sales_order_items").insert(item).execute()
                
                curr_inv = supabase.table("inventory").select("stock_qty").eq("warehouse_id", selected_wh_id).eq("product_id", item["product_id"]).execute().data[0]
                new_qty = curr_inv["stock_qty"] - item["qty"]
                supabase.table("inventory").update({"stock_qty": new_qty}).eq("warehouse_id", selected_wh_id).eq("product_id", item["product_id"]).execute()
                
            st.success("출고/납품 발주서가 정상적으로 등록되었습니다!")
            st.rerun()
