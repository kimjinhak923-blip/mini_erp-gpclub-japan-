import streamlit as st

st.set_page_config(page_title="재고관리(입출고)", layout="wide")

import datetime
import io
import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()
user = st.session_state.get("logged_in_user")

st.title("📦 재고 입출고 및 출고 등록")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📤 일반 출고 등록 (제품/집기 선택)", "📥 개별 입고 등록", "📁 엑셀 대량 업로드"])

# --- [TAB 1] 출고 등록 ---
with tab1:
    st.subheader("📋 출고 지시 및 발주 등록")

    if "out_items_count" not in st.session_state:
        st.session_state.out_items_count = 1

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        out_wh = st.selectbox("출고 창고", ["SAGAWA", "L&K", "大吉商事"])
        order_no = st.text_input("발주번호", value="PO-20260813-001")
        order_code = st.text_input("발주관리번호", value="20260813-01")
    with col_h2:
        cli_names = [c["client_name"] for c in st.session_state.get("clients", [])]
        sel_client = st.selectbox("거래처 선택", cli_names if cli_names else ["등록된 거래처 없음"])
        order_date = st.date_input("발주일", datetime.date.today())
        delivery_date = st.date_input("납품 희망일", datetime.date.today())
    with col_h3:
        dest_name = st.text_input("납품처명", value="도쿄 물류 센터")
        dest_zip = st.text_input("우편번호", value="100-0001")
        dest_addr = st.text_input("납품처 주소", value="東京都千代田区1-1")
        dest_tel = st.text_input("납품처 전화번호", value="03-1234-5678")

    st.markdown("---")
    st.write("##### 📦 출고 등록 품목 목록")

    master_prods = st.session_state.get("master_products", [])
    master_fixs = st.session_state.get("master_fixtures", [])

    prod_options = [f"{p['product_name']} (곽:{p.get('box_jan_code', p.get('jan_code',''))})" for p in master_prods]
    fix_options = [f"{f['fixture_name']} (창고:{f['warehouse']})" for f in master_fixs]

    items_data = []

    for i in range(st.session_state.out_items_count):
        st.markdown(f"**품목 #{i+1}**")
        c_cat, c_p, c_qty, c_box, c_price, c_amt, c_purp = st.columns([1.2, 2.5, 1, 1, 1.2, 1.2, 1])

        with c_cat:
            item_cat = st.selectbox("구분", ["제품", "집기"], key=f"cat_{i}")

        with c_p:
            if item_cat == "제품":
                selected_str = st.selectbox(f"상품 선택 #{i+1}", prod_options if prod_options else ["등록된 상품 없음"], key=f"p_select_{i}")
                p_name = selected_str.split(" (")[0] if " (" in selected_str else selected_str
                matched_p = next((p for p in master_prods if p["product_name"] == p_name), None)
                jan_disp = matched_p.get("box_jan_code", matched_p.get("jan_code", "")) if matched_p else ""
                single_jan = matched_p.get("single_jan_code", "-") if matched_p else "-"
                st.caption(f"곽 JAN: `{jan_disp}` | 낱장 JAN: `{single_jan}`")
            else:
                selected_str = st.selectbox(f"집기 선택 #{i+1}", fix_options if fix_options else ["등록된 집기 없음"], key=f"f_select_{i}")
                p_name = selected_str.split(" (")[0] if " (" in selected_str else selected_str
                matched_p = next((f for f in master_fixs if f["fixture_name"] == p_name), None)
                jan_disp = "-"
                st.caption("🎪 집기 품목 (무상 출고)")

        with c_qty:
            qty = st.number_input(f"수량 #{i+1}", min_value=1, value=10, key=f"qty_{i}")

        with c_box:
            if item_cat == "제품" and matched_p:
                units_per_box = matched_p.get("units_per_box", 1)
                box_count = round(qty / units_per_box, 2)
                box_disp = f"{box_count} Box"
            else:
                box_count = 0
                box_disp = "-"
            st.text_input(f"Box 수량 #{i+1}", value=box_disp, disabled=True, key=f"box_{i}")

        with c_purp:
            if item_cat == "제품":
                purpose = st.selectbox(f"용도 #{i+1}", ["납품", "FOC", "샘플"], key=f"purp_{i}")
            else:
                purpose = "집기출고"
                st.text_input(f"용도 #{i+1}", value="집기출고", disabled=True, key=f"purp_dis_{i}")

        with c_price:
            if item_cat == "제품" and purpose == "납품":
                custom_p = next((cp for cp in st.session_state.get("client_products", []) if cp["client_name"] == sel_client and cp.get("product_name") == p_name), None)
                unit_price = custom_p["custom_supply_price"] if custom_p else (matched_p["supply_price_jpy"] if matched_p else 0)
                price_disp = f"¥{unit_price:,.0f}"
                calc_amt = unit_price * qty
            elif item_cat == "제품":
                unit_price = 0
                price_disp = purpose
                calc_amt = 0
            else:
                unit_price = 0
                price_disp = "무상(집기)"
                calc_amt = 0

            st.text_input(f"공급단가 #{i+1}", value=price_disp, disabled=True, key=f"price_{i}")

        with c_amt:
            amt_disp = f"¥{calc_amt:,.0f}" if (item_cat == "제품" and purpose == "납품") else price_disp
            st.text_input(f"금액 #{i+1}", value=amt_disp, disabled=True, key=f"amt_{i}")

        items_data.append({
            "item_category": item_cat,
            "p_name": p_name,
            "jan": jan_disp,
            "qty": qty,
            "box_qty": box_count,
            "unit_price": unit_price,
            "total_amount": calc_amt,
            "purpose": purpose,
        })

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.session_state.out_items_count < 30:
            if st.button("➕ 품목 추가", use_container_width=True):
                st.session_state.out_items_count += 1
                st.rerun()
    with col_btn2:
        if st.session_state.out_items_count > 1:
            if st.button("➖ 품목 삭제"):
                st.session_state.out_items_count -= 1
                st.rerun()

    st.markdown("---")

    total_prod_count = len(items_data)
    total_out_qty = sum(item["qty"] for item in items_data)
    total_out_box = sum(item["box_qty"] for item in items_data)
    total_order_amount = sum(item["total_amount"] for item in items_data)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("등록 품목 수", f"{total_prod_count:,} 개")
    m2.metric("총 출고 수량", f"{total_out_qty:,} 개")
    m3.metric("총 출고 Box 수량", f"{total_out_box:,.2f} Box")
    m4.metric("총 발주 금액 (무상 제외)", f"¥{total_order_amount:,.0f}")

    if st.button("🚀 출고 확정 및 저장", type="primary", use_container_width=True):
        for item in items_data:
            st.session_state.stock_logs.append({
                "date": str(order_date),
                "delivery_date": str(delivery_date),
                "type": "출고",
                "item_category": item["item_category"],
                "purpose": item["purpose"],
                "jan_code": item["jan"],
                "product_name": item["p_name"],
                "qty": item["qty"],
                "box_qty": item["box_qty"],
                "unit_price": item["unit_price"],
                "total_amount": item["total_amount"],
                "warehouse": out_wh,
                "order_no": order_no,
                "order_code": order_code,
                "status": "출고완료",
                "client_name": sel_client,
                "destination": f"[{dest_name}] {dest_addr} (Tel: {dest_tel})",
                "worker": user["name"] if user else "관리자",
            })

            # 제품인 경우 재고 차감
            if item["item_category"] == "제품":
                stk = next((s for s in st.session_state.warehouse_stocks if s["warehouse"] == out_wh and s["jan_code"] == item["jan"]), None)
                if stk:
                    stk["stock_qty"] -= item["qty"]

        st.success("출고 등록 완료 및 집기/제품 이력이 정상 등록되었습니다!")
        st.session_state.out_items_count = 1
        st.rerun()

# --- [TAB 2] 개별 입고 등록 ---
with tab2:
    st.subheader("📥 개별 입고 등록")
    in_wh = st.selectbox("입고 창고", ["SAGAWA", "L&K", "大吉商事"], key="in_wh_sel")
    m_prods = st.session_state.get("master_products", [])
    m_opts = [f"{p['product_name']} ({p.get('box_jan_code', p.get('jan_code',''))})" for p in m_prods]
    sel_in_prod = st.selectbox("상품 선택 (마스터 등록 상품)", m_opts if m_opts else ["상품 없음"])
    
    p_name_in = sel_in_prod.split(" (")[0] if " (" in sel_in_prod else sel_in_prod
    matched_in_p = next((p for p in m_prods if p["product_name"] == p_name_in), None)

    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        in_qty = st.number_input("입고 수량", min_value=1, value=100)
    with col_i2:
        default_cost = matched_in_p.get("supply_price_jpy", 0) if matched_in_p else 0
        in_unit_cost = st.number_input("매입 단가 (원/엔)", min_value=0, value=default_cost)
    with col_i3:
        in_purpose = st.selectbox("용도", ["매입", "FOC"])

    total_in_cost = in_qty * in_unit_cost if in_purpose == "매입" else 0
    st.info(f"💡 총 매입 금액: **¥{total_in_cost:,.0f}** ({'FOC 무상 입고' if in_purpose == 'FOC' else '자동 연산'})")

    if st.button("📥 입고 등록 실행", type="primary"):
        jan_in = matched_in_p.get("box_jan_code", matched_in_p.get("jan_code", "")) if matched_in_p else ""
        st.session_state.stock_logs.append({
            "date": str(datetime.date.today()),
            "type": "입고",
            "item_category": "제품",
            "purpose": in_purpose,
            "jan_code": jan_in,
            "product_name": p_name_in,
            "qty": in_qty,
            "box_qty": round(in_qty / (matched_in_p["units_per_box"] if matched_in_p else 1), 2),
            "unit_price": in_unit_cost,
            "total_amount": total_in_cost,
            "warehouse": in_wh,
            "order_no": "IN-MANUAL",
            "order_code": "-",
            "status": "입고완료",
            "client_name": "-",
            "destination": in_wh,
            "worker": user["name"] if user else "관리자",
        })

        stk = next((s for s in st.session_state.warehouse_stocks if s["warehouse"] == in_wh and s["jan_code"] == jan_in), None)
        if stk:
            stk["stock_qty"] += in_qty
        else:
            st.session_state.warehouse_stocks.append({
                "warehouse": in_wh,
                "jan_code": jan_in,
                "product_name": p_name_in,
                "stock_qty": in_qty
            })

        st.success("입고 처리가 완료되었습니다.")
        st.rerun()

# --- [TAB 3] 엑셀 대량 업로드 ---
with tab3:
    st.subheader("📁 1~2년치 입출고 데이터 엑셀 대량 업로드")
    template_df = pd.DataFrame([{
        "발주일/납품일": str(datetime.date.today()),
        "구분(입고/출고)": "출고",
        "용도(납품/샘플/FOC)": "납품",
        "상품명": "프리미엄 수분 크림 50ml",
        "수량": 100,
        "거래처명": "(주)파트너스 코리아",
        "납품처명": "도쿄 물류센터 3번 랙",
        "창고명": "SAGAWA",
        "발주번호": "PO-2026-001",
        "발주관리코드": "ORD-001",
        "상태": "출고완료",
    }])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        template_df.to_excel(writer, index=False, sheet_name="입출고대량등록양식")

    st.download_button(
        label="📥 엑셀 업로드 양식 다운로드 (.xlsx)",
        data=buffer.getvalue(),
        file_name="ERP_Stock_Import_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
