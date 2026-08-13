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

tab1, tab2, tab3 = st.tabs(["📤 일반 출고 등록 (품목 동적 추가)", "📥 개별 입고 등록", "📁 엑셀 대량 업로드"])

# ==========================================
# [TAB 1] 일반 출고 등록 (최대 30개 동적 추가)
# ==========================================
with tab1:
    st.subheader("📋 출고 지시 및 발주 등록")

    # 기본 정보 세션 유지
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
    prod_options = [f"{p['product_name']} ({p['jan_code']})" for p in master_prods]

    items_data = []

    # 동적 품목 행 생성
    for i in range(st.session_state.out_items_count):
        st.markdown(f"**품목 #{i+1}**")
        c_p, c_qty, c_box, c_price, c_amt, c_purp = st.columns([3, 1, 1, 1.5, 1.5, 1])

        with c_p:
            selected_p_str = st.selectbox(f"상품 선택 #{i+1}", prod_options if prod_options else ["상품 없음"], key=f"p_select_{i}")
            
            # 선택된 상품 마스터 데이터 매칭
            jan = selected_p_str.split("(")[-1].replace(")", "") if "(" in selected_p_str else ""
            matched_p = next((p for p in master_prods if p["jan_code"] == jan), None)
            
            if matched_p:
                st.caption(f"바코드(JAN): `{matched_p['jan_code']}`")

        with c_qty:
            qty = st.number_input(f"수량 #{i+1}", min_value=1, value=60, key=f"qty_{i}")

        with c_box:
            units_per_box = matched_p["units_per_box"] if matched_p else 1
            box_count = round(qty / units_per_box, 2)
            st.text_input(f"Box 수량 #{i+1}", value=f"{box_count} Box ({units_per_box}/Box)", disabled=True, key=f"box_{i}")

        with c_purp:
            purpose = st.selectbox(f"용도 #{i+1}", ["납품", "FOC", "샘플"], key=f"purp_{i}")

        with c_price:
            if purpose == "납품":
                # 거래처 등록 단가 매칭
                custom_p = next((cp for cp in st.session_state.get("client_products", []) if cp["client_name"] == sel_client and cp.get("jan_code") == jan), None)
                unit_price = custom_p["custom_supply_price"] if custom_p else (matched_p["supply_price_jpy"] if matched_p else 0)
                price_disp = f"¥{unit_price:,.0f}"
                calc_amt = unit_price * qty
            else:
                unit_price = 0
                price_disp = purpose  # FOC 또는 샘플로 출력
                calc_amt = 0  # 합산 제외

            st.text_input(f"공급단가 #{i+1}", value=price_disp, disabled=True, key=f"price_{i}")

        with c_amt:
            amt_disp = f"¥{calc_amt:,.0f}" if purpose == "납품" else purpose
            st.text_input(f"금액 #{i+1}", value=amt_disp, disabled=True, key=f"amt_{i}")

        items_data.append({
            "p_name": matched_p["product_name"] if matched_p else "",
            "jan": jan,
            "qty": qty,
            "box_qty": box_count,
            "unit_price": unit_price,
            "total_amount": calc_amt,
            "purpose": purpose,
            "price_disp": price_disp
        })

    # + 버튼 (최대 30개까지)
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

    # 하단 총 합산 영역
    total_prod_count = len(items_data)
    total_out_qty = sum(item["qty"] for item in items_data)
    total_out_box = sum(item["box_qty"] for item in items_data)
    total_order_amount = sum(item["total_amount"] for item in items_data)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("등록 품목 수", f"{total_prod_count:,} 개")
    m2.metric("총 출고 수량", f"{total_out_qty:,} 개")
    m3.metric("총 출고 Box 수량", f"{total_out_box:,.2f} Box")
    m4.metric("총 발주 금액 (FOC/샘플 제외)", f"¥{total_order_amount:,.0f}")

    if st.button("🚀 출고 확정 및 저장", type="primary", use_container_width=True):
        for item in items_data:
            st.session_state.stock_logs.append({
                "date": str(order_date),
                "delivery_date": str(delivery_date),
                "type": "출고",
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
            
            # 재고 차감
            stk = next((s for s in st.session_state.warehouse_stocks if s["warehouse"] == out_wh and s["jan_code"] == item["jan"]), None)
            if stk:
                stk["stock_qty"] -= item["qty"]

        st.success("출고 처리 및 이력이 정상적으로 저장되었습니다!")
        st.session_state.out_items_count = 1
        st.rerun()

# ==========================================
# [TAB 2] 개별 입고 등록 (매입/FOC & 매입단가 연동)
# ==========================================
with tab2:
    st.subheader("📥 개별 입고 등록")
    
    in_wh = st.selectbox("입고 창고", ["SAGAWA", "L&K", "大吉商事"], key="in_wh_sel")
    
    m_prods = st.session_state.get("master_products", [])
    m_opts = [f"{p['product_name']} ({p['jan_code']})" for p in m_prods]
    sel_in_prod = st.selectbox("상품 선택 (마스터 등록 상품)", m_opts if m_opts else ["상품 없음"])
    
    jan_in = sel_in_prod.split("(")[-1].replace(")", "") if "(" in sel_in_prod else ""
    matched_in_p = next((p for p in m_prods if p["jan_code"] == jan_in), None)

    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        in_qty = st.number_input("입고 수량", min_value=1, value=100)
    with col_i2:
        default_cost = matched_in_p.get("supply_price_jpy", 0) if matched_in_p else 0
        in_unit_cost = st.number_input("매입 단가 (원/엔)", min_value=0, value=default_cost)
    with col_i3:
        in_purpose = st.selectbox("용도", ["매입", "FOC"])

    # 총 매입액 계산
    total_in_cost = in_qty * in_unit_cost if in_purpose == "매입" else 0
    st.info(f"💡 총 매입 금액: **¥{total_in_cost:,.0f}** ({'FOC 무상 입고' if in_purpose == 'FOC' else '자동 연산'})")

    if st.button("📥 입고 등록 실행", type="primary"):
        st.session_state.stock_logs.append({
            "date": str(datetime.date.today()),
            "type": "입고",
            "purpose": in_purpose,
            "jan_code": jan_in,
            "product_name": matched_in_p["product_name"] if matched_in_p else "",
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

        # 창고 재고 증가
        stk = next((s for s in st.session_state.warehouse_stocks if s["warehouse"] == in_wh and s["jan_code"] == jan_in), None)
        if stk:
            stk["stock_qty"] += in_qty
        else:
            st.session_state.warehouse_stocks.append({
                "warehouse": in_wh,
                "jan_code": jan_in,
                "product_name": matched_in_p["product_name"] if matched_in_p else "",
                "stock_qty": in_qty
            })

        st.success("입고 처리가 완료되었습니다.")
        st.rerun()

# ==========================================
# [TAB 3] 엑셀 대량 업로드 (기존 기능 유지)
# ==========================================
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
