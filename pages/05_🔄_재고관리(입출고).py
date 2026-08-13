import streamlit as st

st.set_page_config(page_title="재고관리(입출고)", page_layout="wide")

import datetime
import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("📦 재고 입출고 처리")
st.markdown("---")

tab1, tab2 = st.tabs(["📥 입고 처리", "📤 출고 처리 (다중 품목)"])

with tab1:
    st.subheader("창고별 입고 등록")
    with st.form("inbound_form"):
        c1, c2 = st.columns(2)
        with c1:
            target_wh = st.selectbox("입고 창고", st.session_state.warehouses)
            p_options = [
                f"{p['product_name']} ({p['jan_code']})"
                for p in st.session_state.master_products
            ]
            sel_p = st.selectbox("입고 상품", p_options if p_options else ["상품 없음"])
        with c2:
            in_qty = st.number_input("입고 수량(EA)", min_value=1, value=100)
            in_memo = st.text_input("입고 메모 / 비고")

        in_sub = st.form_submit_button("입고 승인 및 반영")
        if in_sub:
            if not p_options:
                st.error("상품이 없습니다.")
            else:
                jan = sel_p.split("(")[-1].replace(")", "")
                p_name = sel_p.split(" (")[0]

                stock_item = next(
                    (
                        s
                        for s in st.session_state.warehouse_stocks
                        if s["warehouse"] == target_wh and s["jan_code"] == jan
                    ),
                    None,
                )
                if stock_item:
                    stock_item["stock_qty"] += in_qty
                else:
                    st.session_state.warehouse_stocks.append({
                        "warehouse": target_wh,
                        "jan_code": jan,
                        "product_name": p_name,
                        "stock_qty": in_qty,
                    })

                st.session_state.stock_logs.append({
                    "date": str(datetime.date.today()),
                    "type": "입고",
                    "warehouse": target_wh,
                    "client_name": "-",
                    "jan_code": jan,
                    "product_name": p_name,
                    "qty": in_qty,
                    "unit_price": 0,
                    "total_amount": 0,
                    "postal_code": "-",
                    "address": "-",
                    "phone": "-",
                    "worker": user["name"],
                    "memo": in_memo,
                })
                st.success("입고 처리가 완료되었습니다.")
                st.rerun()

with tab2:
    st.subheader("거래처 출고 및 배송지 입력")
    c1, c2 = st.columns(2)
    with c1:
        out_wh = st.selectbox("출하 창고", st.session_state.warehouses, key="out_wh_s")
        cli_opts = [c["client_name"] for c in st.session_state.clients]
        sel_cli = st.selectbox(
            "거래처 선택", cli_opts if cli_opts else ["거래처 없음"]
        )

    client_obj = next(
        (c for c in st.session_state.clients if c["client_name"] == sel_cli), None
    )

    with c2:
        dest_postal = st.text_input(
            "배송지 우편번호",
            value=client_obj["postal_code"] if client_obj else "",
        )
        dest_addr = st.text_input(
            "배송지 주소", value=client_obj["address"] if client_obj else ""
        )
        dest_phone = st.text_input(
            "수령인 전화번호", value=client_obj["phone"] if client_obj else ""
        )

    st.markdown("---")
    st.write("🛒 **출고 품목 선택**")

    wh_stocks = [
        s for s in st.session_state.warehouse_stocks if s["warehouse"] == out_wh
    ]
    if not wh_stocks:
        st.warning("선택한 창고에 출고 가능한 재고가 없습니다.")
    else:
        out_p_opts = [
            f"{s['product_name']} (재고: {s['stock_qty']}개 | JAN: {s['jan_code']})"
            for s in wh_stocks
        ]
        sel_out_p = st.selectbox("출고할 상품 선택", out_p_opts)
        out_qty = st.number_input("출고 수량", min_value=1, value=10)

        jan_out = sel_out_p.split("JAN: ")[-1].replace(")", "")
        p_obj = next(
            (p for p in st.session_state.master_products if p["jan_code"] == jan_out),
            None,
        )

        custom_p = next(
            (
                cp
                for cp in st.session_state.client_products
                if cp["client_name"] == sel_cli and cp["jan_code"] == jan_out
            ),
            None,
        )

        unit_p = (
            custom_p["custom_supply_price"]
            if custom_p
            else (p_obj["supply_price_jpy"] if p_obj else 0)
        )
        st.info(f"적용 공급단가: ¥{unit_p:,} / 총 출고 금액: ¥{unit_p * out_qty:,}")

        if st.button("📤 출고 확정"):
            stock_item = next(
                (s for s in wh_stocks if s["jan_code"] == jan_out), None
            )
            if stock_item["stock_qty"] < out_qty:
                st.error("재고 수량이 부족합니다.")
            else:
                stock_item["stock_qty"] -= out_qty
                st.session_state.stock_logs.append({
                    "date": str(datetime.date.today()),
                    "type": "출고",
                    "warehouse": out_wh,
                    "client_name": sel_cli,
                    "jan_code": jan_out,
                    "product_name": stock_item["product_name"],
                    "qty": out_qty,
                    "unit_price": unit_p,
                    "total_amount": unit_p * out_qty,
                    "postal_code": dest_postal,
                    "address": dest_addr,
                    "phone": dest_phone,
                    "worker": user["name"],
                    "memo": "정상 출고",
                })
                st.success("출고 처리 및 이력 기록이 완료되었습니다.")
                st.rerun()
