import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

st.set_page_config(page_title="입출고 등록 및 이력 관리", layout="wide")
render_sidebar()

st.title("📜 입출고 등록 및 통합 이력 관리")
st.markdown("---")

# -----------------------------------------------------------------------------
# 1. 세션 상태 초기화 및 샘플 데이터 보장
# -----------------------------------------------------------------------------
if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = []

if "warehouses" not in st.session_state:
    st.session_state.warehouses = ["SAGAWA", "L&K", "大吉商事"]

if "clients" not in st.session_state:
    st.session_state.clients = ["A상사", "B유통", "C스토어"]

# 거래처별 등록 상품 단가 데이터 (연동용)
if "client_products" not in st.session_state:
    st.session_state.client_products = [
        {"client_name": "A상사", "product_name": "세럼 50ml", "jan_code": "4580000000001", "unit_price": 12000},
        {"client_name": "A상사", "product_name": "크림 100ml", "jan_code": "4580000000002", "unit_price": 25000},
        {"client_name": "B유통", "product_name": "세럼 50ml", "jan_code": "4580000000001", "unit_price": 11500},
    ]

# 탭 구성: 신규 입출고 등록 / 이력 조회 및 수정
tab1, tab2 = st.tabs(["➕ 입출고 신규 등록", "📜 이력 조회 및 수정/삭제"])

# -----------------------------------------------------------------------------
# TAB 1: 입출고 신규 등록 (거래처 단가 자동 연동 & 천 단위 표기)
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("📦 입출고 등록")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        log_type = st.radio("입출고 구분", ["입고", "출고"], horizontal=True)
        warehouse = st.selectbox("창고 선택", st.session_state.warehouses)
        client_name = st.selectbox("거래처 선택", st.session_state.clients)

    # 선택된 거래처에 등록된 상품 목록 추출
    client_prods = [
        cp for cp in st.session_state.client_products 
        if cp.get("client_name") == client_name
    ]
    
    # 거래처 등록 상품이 없을 경우 마스터 상품 활용 안내
    if not client_prods:
        st.warning(f"⚠️ '{client_name}' 거래처에 등록된 단가 정보가 없습니다. (기본 마스터 상품 정보를 사용합니다.)")
        master_prods = st.session_state.get("master_products", [])
        prod_options = [p.get("product_name") for p in master_prods]
    else:
        prod_options = [p.get("product_name") for p in client_prods]

    with col_t2:
        if prod_options:
            selected_prod_name = st.selectbox("상품 선택", prod_options)
            
            # 선택된 거래처/상품의 단가(유닛프라이스) 자동 매핑
            matched_item = next(
                (cp for cp in client_prods if cp.get("product_name") == selected_prod_name),
                None
            )
            
            # 단가 자동 연동
            if matched_item:
                default_unit_price = int(matched_item.get("unit_price", 0))
                jan_code = matched_item.get("jan_code", "")
            else:
                # 마스터 상품에서 가져오기
                m_item = next((mp for mp in st.session_state.get("master_products", []) if mp.get("product_name") == selected_prod_name), {})
                default_unit_price = int(m_item.get("cost_price_krw", 0))
                jan_code = m_item.get("jan_code", "")

            qty = st.number_input("수량 (EA)", min_value=1, value=100, step=10)
            unit_price = st.number_input("유닛프라이스 (공급단가)", min_value=0, value=default_unit_price, step=500)
            
            # 수량 * 유닛프라이스 자동 계산
            total_amount = qty * unit_price
            
            # 요약 정보 표기 (천 단위 쉼표 0,000 적용)
            st.info(f"💡 **총 금액**: **{total_amount:,.0f}** 원 (수량 {qty:,} EA × 단가 {unit_price:,.0f} 원)")

            if st.button("🚀 입출고 내역 등록", type="primary"):
                new_log = {
                    "type": log_type,
                    "warehouse": warehouse,
                    "client_name": client_name,
                    "product_name": selected_prod_name,
                    "jan_code": jan_code,
                    "qty": qty,
                    "unit_price": unit_price,
                    "total_amount": total_amount,
                    "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                }
                st.session_state.stock_logs.append(new_log)
                st.success(f"[{selected_prod_name}] {log_type} 등록이 완료되었습니다! (총액: {total_amount:,.0f}원)")
                st.rerun()
        else:
            st.error("등록할 수 있는 상품이 없습니다. 마스터 상품 또는 거래처 상품을 먼저 등록해 주세요.")

# -----------------------------------------------------------------------------
# TAB 2: 이력 조회 및 수정/삭제 (천 단위 표기 & 자동 계산)
# -----------------------------------------------------------------------------
with tab2:
    if not st.session_state.stock_logs:
        st.info("입출고 이력이 존재하지 않습니다.")
    else:
        df_logs = pd.DataFrame(st.session_state.stock_logs)
        df_logs["_orig_idx"] = df_logs.index
        df_logs["선택"] = False

        # 필터 영역
        c1, c2, c3 = st.columns(3)
        with c1:
            type_filter = st.multiselect("구분 필터", ["입고", "출고"], default=["입고", "출고"])
        with c2:
            existing_whs = list(set(st.session_state.warehouses + df_logs.get("warehouse", pd.Series()).tolist()))
            wh_filter = st.multiselect("창고 필터", existing_whs, default=existing_whs)
        with c3:
            search_kw = st.text_input("검색어 (상품명, JAN, 거래처)", "")

        filtered_df = df_logs[
            (df_logs["type"].isin(type_filter)) & (df_logs["warehouse"].isin(wh_filter))
        ].copy()

        if search_kw:
            filtered_df = filtered_df[
                filtered_df.get("product_name", pd.Series()).astype(str).str.contains(search_kw, na=False)
                | filtered_df.get("jan_code", pd.Series()).astype(str).str.contains(search_kw, na=False)
                | filtered_df.get("client_name", pd.Series()).astype(str).str.contains(search_kw, na=False)
            ]

        if filtered_df.empty:
            st.warning("조건에 일치하는 이력이 없습니다.")
        else:
            st.caption("💡 수량/단가 변경 시 **총 금액이 자동으로 계산**되며, 숫자는 모두 **천 단위(0,000)**로 표시됩니다.")

            # 열 정렬
            cols_order = ["선택", "type", "date", "warehouse", "client_name", "product_name", "jan_code", "qty", "unit_price", "total_amount"]
            cols_exist = [c for c in cols_order if c in filtered_df.columns]
            
            # 수량 * 단가 재계산 처리
            filtered_df["total_amount"] = filtered_df["qty"] * filtered_df["unit_price"]

            # 데이터 에디터 (천 단위 포맷팅 %,d 설정)
            edited_df = st.data_editor(
                filtered_df[cols_exist],
                use_container_width=True,
                column_config={
                    "선택": st.column_config.CheckboxColumn("선택", default=False),
                    "type": st.column_config.SelectboxColumn("구분", options=["입고", "출고"], required=True),
                    "warehouse": st.column_config.SelectboxColumn("창고", options=existing_whs),
                    "qty": st.column_config.NumberColumn("수량 (EA)", min_value=1, step=1, format="%,d"),
                    "unit_price": st.column_config.NumberColumn("유닛프라이스 (공급가)", min_value=0, format="%,d"),
                    "total_amount": st.column_config.NumberColumn("총 금액", min_value=0, format="%,d", disabled=True),
                },
                key="stock_logs_editor_v2",
            )

            btn_col1, btn_col2, _ = st.columns([2, 2, 6])

            # 변경사항 저장
            with btn_col1:
                if st.button("💾 수정사항 저장", type="primary", use_container_width=True):
                    for idx, row in edited_df.iterrows():
                        orig_idx = filtered_df.loc[idx, "_orig_idx"]
                        
                        # 총액 재계산
                        updated_dict = row.drop(["선택"], errors="ignore").to_dict()
                        updated_dict["total_amount"] = updated_dict["qty"] * updated_dict["unit_price"]
                        
                        st.session_state.stock_logs[orig_idx].update(updated_dict)

                    st.success("수정사항 및 총 금액이 자동 계산되어 저장되었습니다.")
                    st.rerun()

            # 선택 항목 삭제
            with btn_col2:
                if st.button("🗑️ 선택 항목 삭제", type="secondary", use_container_width=True):
                    selected_rows = edited_df[edited_df["선택"] == True]
                    if selected_rows.empty:
                        st.warning("삭제할 항목을 먼저 체크해 주세요.")
                    else:
                        delete_indices = [filtered_df.loc[r_idx, "_orig_idx"] for r_idx in selected_rows.index]
                        st.session_state.stock_logs = [
                            log for idx, log in enumerate(st.session_state.stock_logs) if idx not in delete_indices
                        ]
                        st.success(f"{len(delete_indices)}건의 이력이 삭제되었습니다.")
                        st.rerun()
