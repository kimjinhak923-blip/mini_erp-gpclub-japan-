import streamlit as st

st.set_page_config(page_title="재고관리(입출고)", layout="wide")

import datetime
import io
import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("📦 재고 입출고 처리 및 엑셀 대량 등록")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 엑셀 대량 등록 (1~2년치 이력)", "📥 개별 입고 등록", "📤 개별 출고 등록"])

# --- TAB 1: 엑셀 대량 등록 ---
with tab1:
    st.subheader("📁 1~2년치 입출고 데이터 엑셀 대량 업로드")
    st.caption("필수 입력 항목만 작성하여 올리시면 상품 마스터 및 거래처 단가를 매칭하여 박스 수량, 금액, 카테고리 등을 자동 계산합니다.")

    # 1. 샘플 양식 다운로드 버튼
    template_df = pd.DataFrame([
        {
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
        }
    ])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        template_df.to_excel(writer, index=False, sheet_name="입출고대량등록양식")

    st.download_button(
        label="📥 엑셀 업로드 양식 다운로드 (.xlsx)",
        data=buffer.getvalue(),
        file_name="ERP_Stock_Import_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown("---")

    # 2. 파일 업로더
    uploaded_file = st.file_uploader("작성한 엑셀 파일(.xlsx, .xls) 또는 CSV 파일을 선택하세요", type=["xlsx", "xls", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)

            st.write("📋 **업로드된 데이터 미리보기**")
            st.dataframe(df_upload.head(10), use_container_width=True)

            if st.button("🚀 데이터 매칭 및 대량 등록 실행", type="primary"):
                success_count = 0
                master_prods = st.session_state.master_products
                clients = st.session_state.clients
                client_prices = st.session_state.client_products

                for _, row in df_upload.iterrows():
                    p_name = str(row.get("상품명", "")).strip()
                    qty = int(row.get("수량", 0))
                    c_name = str(row.get("거래처명", "")).strip()
                    wh_name = str(row.get("창고명", "SAGAWA")).strip()
                    purpose = str(row.get("용도(납품/샘플/FOC)", "납품")).strip()
                    io_type = str(row.get("구분(입고/출고)", "출고")).strip()

                    # 마스터 상품 자동 매칭
                    matched_p = next((p for p in master_prods if p["product_name"] == p_name), None)
                    jan = matched_p["jan_code"] if matched_p else "UNKNOWN"
                    category = matched_p["category"] if matched_p else "기타"
                    units_per_box = matched_p["units_per_box"] if matched_p else 1

                    # 박스 수량 자동 계산
                    box_qty = round(qty / units_per_box, 2) if units_per_box > 0 else qty

                    # 제품 단가 자동 매칭 (거래처 전용 단가 -> 없으면 마스터 공급가)
                    custom_p = next((cp for cp in client_prices if cp["client_name"] == c_name and cp["product_name"] == p_name), None)
                    if custom_p:
                        unit_price = custom_p["custom_supply_price"]
                    else:
                        unit_price = matched_p["supply_price_jpy"] if matched_p else 0

                    total_amount = unit_price * qty

                    # 이력 세션에 저장
                    st.session_state.stock_logs.append({
                        "date": str(row.get("발주일/납품일", str(datetime.date.today()))),
                        "type": io_type,
                        "purpose": purpose,
                        "jan_code": jan,
                        "product_name": p_name,
                        "category": category,
                        "qty": qty,
                        "box_qty": box_qty,
                        "unit_price": unit_price,
                        "total_amount": total_amount,
                        "warehouse": wh_name,
                        "order_no": str(row.get("발주번호", "-")),
                        "order_code": str(row.get("발주관리코드", "-")),
                        "status": str(row.get("상태", "완료")),
                        "client_name": c_name,
                        "destination": str(row.get("납품처명", "-")),
                        "worker": user["name"],
                    })

                    # 재고 반영
                    stk = next((s for s in st.session_state.warehouse_stocks if s["warehouse"] == wh_name and s["product_name"] == p_name), None)
                    if stk:
                        if io_type == "입고":
                            stk["stock_qty"] += qty
                        else:
                            stk["stock_qty"] -= qty
                    else:
                        st.session_state.warehouse_stocks.append({
                            "warehouse": wh_name,
                            "jan_code": jan,
                            "product_name": p_name,
                            "stock_qty": qty if io_type == "입고" else -qty,
                        })

                    success_count += 1

                st.success(f"🎉 총 {success_count}건의 데이터가 성공적으로 등록 및 자동 계산되었습니다!")
                st.rerun()

        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {e}")

# --- TAB 2 & TAB 3: 개별 처리 (기존 기능 완전 복구) ---
with tab2:
    st.subheader("개별 입고 처리")
    with st.form("single_in_form"):
        c1, c2 = st.columns(2)
        with c1:
            in_wh = st.selectbox("입고 창고", st.session_state.warehouses)
            p_opts = [f"{p['product_name']} ({p['jan_code']})" for p in st.session_state.master_products]
            sel_in_p = st.selectbox("상품 선택", p_opts if p_opts else ["상품 없음"])
        with c2:
            in_qty = st.number_input("입고 수량(EA)", min_value=1, value=100)
            in_purpose = st.selectbox("용도", ["납품", "샘플", "FOC"])

        if st.form_submit_button("입고 등록"):
            p_name = sel_in_p.split(" (")[0]
            jan = sel_in_p.split("(")[-1].replace(")", "")
            matched_p = next((p for p in st.session_state.master_products if p["jan_code"] == jan), None)

            st.session_state.stock_logs.append({
                "date": str(datetime.date.today()),
                "type": "입고",
                "purpose": in_purpose,
                "jan_code": jan,
                "product_name": p_name,
                "category": matched_p["category"] if matched_p else "-",
                "qty": in_qty,
                "box_qty": round(in_qty / matched_p["units_per_box"], 2) if matched_p else in_qty,
                "unit_price": matched_p["supply_price_jpy"] if matched_p else 0,
                "total_amount": (matched_p["supply_price_jpy"] if matched_p else 0) * in_qty,
                "warehouse": in_wh,
                "order_no": "MANUAL-IN",
                "order_code": "-",
                "status": "입고완료",
                "client_name": "-",
                "destination": in_wh,
                "worker": user["name"],
            })
            st.success("입고 완료되었습니다.")
            st.rerun()

with tab3:
    st.subheader("개별 출고 처리")
    with st.form("single_out_form"):
        c1, c2 = st.columns(2)
        with c1:
            out_wh = st.selectbox("출고 창고", st.session_state.warehouses, key="single_out_wh")
            cli_opts = [c["client_name"] for c in st.session_state.clients]
            sel_cli = st.selectbox("거래처 선택", cli_opts if cli_opts else ["없음"])
            p_opts = [f"{p['product_name']} ({p['jan_code']})" for p in st.session_state.master_products]
            sel_out_p = st.selectbox("상품 선택", p_opts if p_opts else ["없음"], key="single_out_p")
        with c2:
            out_qty = st.number_input("출고 수량(EA)", min_value=1, value=10)
            out_purpose = st.selectbox("용도", ["납품", "샘플", "FOC"], key="single_out_purp")
            dest = st.text_input("납품처 주소/메모")

        if st.form_submit_button("출고 확정"):
            p_name = sel_out_p.split(" (")[0]
            jan = sel_out_p.split("(")[-1].replace(")", "")
            matched_p = next((p for p in st.session_state.master_products if p["jan_code"] == jan), None)

            # 전용 단가 확인
            custom_p = next((cp for cp in st.session_state.client_products if cp["client_name"] == sel_cli and cp["jan_code"] == jan), None)
            u_price = custom_p["custom_supply_price"] if custom_p else (matched_p["supply_price_jpy"] if matched_p else 0)

            st.session_state.stock_logs.append({
                "date": str(datetime.date.today()),
                "type": "출고",
                "purpose": out_purpose,
                "jan_code": jan,
                "product_name": p_name,
                "category": matched_p["category"] if matched_p else "-",
                "qty": out_qty,
                "box_qty": round(out_qty / matched_p["units_per_box"], 2) if matched_p else out_qty,
                "unit_price": u_price,
                "total_amount": u_price * out_qty,
                "warehouse": out_wh,
                "order_no": "MANUAL-OUT",
                "order_code": "-",
                "status": "출고완료",
                "client_name": sel_cli,
                "destination": dest,
                "worker": user["name"],
            })
            st.success("출고 처리되었습니다.")
            st.rerun()
