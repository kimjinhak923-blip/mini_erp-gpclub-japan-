import datetime
import pytz
import streamlit as st

st.set_page_config(page_title="재고관리", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

user = st.session_state.logged_in_user
is_visitor = user.get("role") == "방문자"

def get_tokyo_time():
    return datetime.datetime.now(pytz.timezone("Asia/Tokyo"))

def update_wh_stock(prod_code, wh_name, qty_change):
    key = f"{prod_code}_{wh_name}"
    current = st.session_state.warehouse_stocks.get(key, 0)
    st.session_state.warehouse_stocks[key] = max(0, current + qty_change)

st.header("🔄 재고관리 (입고 / 출고 등록)")
tokyo_now = get_tokyo_time()

mode = st.radio("작업 선택", ["📥 입고 등록", "📤 출고 등록 (우편번호 포함)"])

if mode == "📥 입고 등록":
    st.subheader("📥 입고 등록")
    if st.session_state.master_products:
        prod_map = {f"[{p['code']}] {p['name']}": p for p in st.session_state.master_products}
        sel_p_label = st.selectbox("상품 선택", list(prod_map.keys()))
        sel_p = prod_map[sel_p_label]

        with st.form("inbound_form"):
            in_wh = st.selectbox("입고 창고 *", st.session_state.warehouses)
            in_jan = st.text_input("JAN 코드", value=sel_p.get("jan_pack", ""))
            in_price = st.number_input("매입단가(엔)", min_value=0, value=int(sel_p["price"]))
            in_qty = st.number_input("입고 수량", min_value=1, value=10)

            if st.form_submit_button("입고 완료", disabled=is_visitor):
                update_wh_stock(sel_p["code"], in_wh, in_qty)
                st.session_state.stock_logs.append({
                    "po_no": f"IN-{tokyo_now.strftime('%Y%m%d%H%M%S')}",
                    "date": tokyo_now.strftime("%Y-%m-%d"),
                    "type": "입고",
                    "wh": in_wh,
                    "client": "-",
                    "prod_name": sel_p["name"],
                    "jan": in_jan,
                    "qty": in_qty,
                    "unit_price": in_price,
                    "total_price": in_price * in_qty,
                    "trade_type": "매입",
                    "manager": user["name"],
                    "zipcode": "-",
                    "ship_to": "-",
                })
                st.success("입고 처리가 완료되었습니다.")
                st.rerun()

else:
    st.subheader("📤 출고 등록 (우편번호 항목 반영)")
    if st.session_state.clients:
        c_names = [c["name"] for c in st.session_state.clients]
        sel_c_name = st.selectbox("1. 거래처 선택", c_names)
        sel_c_obj = next(c for c in st.session_state.clients if c["name"] == sel_c_name)
        avail_cps = [cp for cp in st.session_state.client_products if cp["client_name"] == sel_c_name]

        if avail_cps:
            st.markdown("---")
            st.subheader("2. Delivery & Ship-to Information (우편번호 포함)")

            c_a, c_b = st.columns(2)
            out_wh = c_a.selectbox("출고 창고 *", st.session_state.warehouses)
            ship_name = c_a.text_input("납품처명 *", value=sel_c_name)
            ship_zip = c_b.text_input("우편번호 *", value=sel_c_obj.get("zipcode", ""))
            ship_addr = c_b.text_input("주소 *", value=sel_c_obj["address"])
            ship_phone = c_a.text_input("전화번호 *", value=sel_c_obj["phone"])

            st.markdown("---")
            st.subheader("3. 출고 대상 제품 선택")
            num_items = st.number_input("품목 개수", min_value=1, max_value=30, value=1)
            cp_labels = [f"{cp['prod_name']} (¥{cp['supply_price']:,})" for cp in avail_cps]

            with st.form("multi_outbound_form"):
                items_out = []
                po_code = f"OUT-{tokyo_now.strftime('%Y%m%d%H%M%S')}"

                for i in range(int(num_items)):
                    col1, col2, col3 = st.columns([3, 2, 2])
                    idx = col1.selectbox(f"제품 #{i+1}", range(len(cp_labels)), format_func=lambda x: cp_labels[x], key=f"o_cp_{i}")
                    t_type = col2.selectbox(f"거래방식 #{i+1}", ["납품", "FOC", "테스터"], key=f"o_tr_{i}")
                    q_val = col3.number_input(f"수량 #{i+1}", min_value=1, value=1, key=f"o_q_{i}")

                    cp_item = avail_cps[idx]
                    u_price = 0 if t_type in ["FOC", "테스터"] else cp_item["supply_price"]
                    items_out.append({
                        "cp": cp_item,
                        "trade_type": t_type,
                        "qty": q_val,
                        "unit_price": u_price,
                        "total": u_price * q_val,
                    })

                if st.form_submit_button("일괄 출고 실행", disabled=is_visitor):
                    for it in items_out:
                        cp_o = it["cp"]
                        matched_m = next((m for m in st.session_state.master_products if m["name"] == cp_o["prod_name"]), None)
                        if matched_m:
                            update_wh_stock(matched_m["code"], out_wh, -it["qty"])

                        st.session_state.stock_logs.append({
                            "po_no": po_code,
                            "date": tokyo_now.strftime("%Y-%m-%d"),
                            "type": "출고",
                            "wh": out_wh,
                            "client": sel_c_name,
                            "prod_name": cp_o["prod_name"],
                            "jan": cp_o.get("jan_pack", ""),
                            "qty": it["qty"],
                            "unit_price": it["unit_price"],
                            "total_price": it["total"],
                            "trade_type": it["trade_type"],
                            "manager": user["name"],
                            "zipcode": ship_zip,
                            "ship_to": f"{ship_name} / {ship_addr} / {ship_phone}",
                        })
                    st.success("출고 완료되었습니다.")
                    st.rerun()
