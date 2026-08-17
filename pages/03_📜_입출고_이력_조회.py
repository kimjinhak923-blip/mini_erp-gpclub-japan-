import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar

st.set_page_config(page_title="입출고 이력 관리", layout="wide")
render_sidebar()

# DB 테이블 초기화
db.init_db()

st.title("📜 입출고 이력 조회 및 수정/삭제")
st.markdown("---")

# 세션 상태 초기화
if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = []

if "warehouses" not in st.session_state:
    st.session_state.warehouses = ["SAGAWA", "L&K", "大吉商事"]

if not st.session_state.stock_logs:
    st.info("등록된 입출고 이력이 존재하지 않습니다.")
else:
    # 원본 데이터 로드
    df_logs = pd.DataFrame(st.session_state.stock_logs)
    
    # 원본 인덱스 보존 및 선택 열 추가
    df_logs["_orig_idx"] = df_logs.index
    df_logs["선택"] = False

    # 총금액 계산 보장 (qty * unit_price)
    if "unit_price" in df_logs.columns and "qty" in df_logs.columns:
        df_logs["total_amount"] = df_logs["qty"].fillna(0) * df_logs["unit_price"].fillna(0)

    # -----------------------------------------------------------------------------
    # 🔍 필터 영역
    # -----------------------------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    with c1:
        type_filter = st.multiselect("구분 필터", ["입고", "출고"], default=["입고", "출고"])
    with c2:
        existing_whs = list(set(st.session_state.warehouses + df_logs.get("warehouse", pd.Series()).tolist()))
        wh_filter = st.multiselect("창고 필터", existing_whs, default=existing_whs)
    with c3:
        search_kw = st.text_input("검색어 (상품명, JAN, 거래처)", "")

    # 필터링 적용
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
        st.warning("조건에 일치하는 입출고 이력이 없습니다.")
    else:
        st.caption("💡 수량/단가 변경 시 **총금액이 자동 계산**되며, 삭제할 항목은 '선택'에 체크 후 삭제 버튼을 누르세요.")

        # 칼럼 순서 정렬 ("선택" 열을 맨 앞으로 배치)
        cols_order = ["선택", "type", "date", "warehouse", "client_name", "product_name", "jan_code", "qty", "unit_price", "total_amount"]
        cols_exist = [c for c in cols_order if c in filtered_df.columns]

        # -----------------------------------------------------------------------------
        # ✏️ 데이터 에디터 (수정, 삭제 및 천 단위 표기)
        # -----------------------------------------------------------------------------
        edited_df = st.data_editor(
            filtered_df[cols_exist],
            use_container_width=True,
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", help="삭제할 항목을 체크하세요.", default=False),
                "type": st.column_config.SelectboxColumn("구분", options=["입고", "출고"], required=True),
                "warehouse": st.column_config.SelectboxColumn("창고", options=existing_whs),
                "qty": st.column_config.NumberColumn("수량 (EA)", min_value=1, step=1, format="%,d"),
                "unit_price": st.column_config.NumberColumn("유닛프라이스 (공급가)", min_value=0, format="%,d"),
                "total_amount": st.column_config.NumberColumn("총 금액", min_value=0, format="%,d", disabled=True),
            },
            key="stock_logs_editor_single_page",
        )

        # -----------------------------------------------------------------------------
        # 💾 작업 버튼 (수정 저장 / 선택 삭제)
        # -----------------------------------------------------------------------------
        btn_col1, btn_col2, _ = st.columns([2, 2, 6])

        # 1. 수정사항 저장
        with btn_col1:
            if st.button("💾 변경사항 저장", type="primary", use_container_width=True):
                for idx, row in edited_df.iterrows():
                    orig_idx = filtered_df.loc[idx, "_orig_idx"]
                    
                    # 수량 * 단가 총액 자동 재계산
                    row_dict = row.drop(["선택"], errors="ignore").to_dict()
                    qty_val = row_dict.get("qty", 0) or 0
                    unit_val = row_dict.get("unit_price", 0) or 0
                    row_dict["total_amount"] = qty_val * unit_val
                    
                    # 기존 세션 업데이트
                    st.session_state.stock_logs[orig_idx].update(row_dict)

                st.success("수정사항이 성공적으로 저장되었습니다.")
                st.rerun()

        # 2. 선택 항목 삭제
        with btn_col2:
            if st.button("🗑️ 선택 항목 삭제", type="secondary", use_container_width=True):
                selected_rows = edited_df[edited_df["선택"] == True]

                if selected_rows.empty:
                    st.warning("삭제할 항목을 먼저 체크해 주세요.")
                else:
                    delete_indices = [filtered_df.loc[r_idx, "_orig_idx"] for r_idx in selected_rows.index]
                    
                    # 세션 리스트에서 대상 인덱스 제거
                    st.session_state.stock_logs = [
                        log for idx, log in enumerate(st.session_state.stock_logs) if idx not in delete_indices
                    ]

                    st.success(f"{len(delete_indices)}건의 이력이 삭제되었습니다.")
                    st.rerun()
