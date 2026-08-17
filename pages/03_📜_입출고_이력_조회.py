import io
import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar

st.set_page_config(page_title="입출고 이력 관리", layout="wide")
render_sidebar()

# DB 및 테이블 초기화
db.init_db()

st.title("📜 입출고 이력 조회 및 수정/삭제")
st.markdown("---")

# =============================================================================
# 1. DB 및 마스터 데이터 로드 (실시간 동기화)
# =============================================================================
# DB에서 최신 입출고 이력 불러오기
db_logs = db.load_stock_logs()
st.session_state.stock_logs = db_logs

# 창고 마스터 로드
warehouses_data = db.load_warehouses()
wh_names = (
    [w.get("warehouse_name") for w in warehouses_data]
    if warehouses_data
    else ["SAGAWA", "L&K", "大吉商事"]
)
st.session_state.warehouses = list(set(wh_names))

# 데이터 존재 여부 확인
if not st.session_state.stock_logs:
    st.info("등록된 입출고 이력이 존재하지 않습니다.")
else:
    # 데이터프레임 생성
    df_logs = pd.DataFrame(st.session_state.stock_logs)

    # 원본 인덱스 보존 및 선택 열 추가
    df_logs["_orig_idx"] = df_logs.index
    df_logs["선택"] = False

    # 수량 및 단가 기본값 처리 및 총금액 계산
    if "qty" in df_logs.columns:
        df_logs["qty"] = pd.to_numeric(df_logs["qty"], errors="coerce").fillna(
            0
        )
    if "unit_price" in df_logs.columns:
        df_logs["unit_price"] = pd.to_numeric(
            df_logs["unit_price"], errors="coerce"
        ).fillna(0)

    df_logs["total_amount"] = df_logs["qty"] * df_logs["unit_price"]

    # 필수 컬럼 보장
    for col in ["jan_code", "client_name", "product_name", "item_category"]:
        if col not in df_logs.columns:
            df_logs[col] = "-"

    # =============================================================================
    # 🔍 2. 필터 및 검색 영역
    # =============================================================================
    c1, c2, c3 = st.columns(3)
    with c1:
        type_filter = st.multiselect(
            "구분 필터", ["입고", "출고"], default=["입고", "출고"]
        )
    with c2:
        existing_whs = list(
            set(
                st.session_state.warehouses
                + df_logs.get("warehouse", pd.Series()).tolist()
            )
        )
        wh_filter = st.multiselect("창고 필터", existing_whs, default=existing_whs)
    with c3:
        search_kw = st.text_input("검색어 (상품명, JAN, 거래처)", "")

    # 필터링 적용
    filtered_df = df_logs[
        (df_logs["type"].isin(type_filter))
        & (df_logs["warehouse"].isin(wh_filter))
    ].copy()

    if search_kw:
        filtered_df = filtered_df[
            filtered_df.get("product_name", pd.Series())
            .astype(str)
            .str.contains(search_kw, na=False)
            | filtered_df.get("jan_code", pd.Series())
            .astype(str)
            .str.contains(search_kw, na=False)
            | filtered_df.get("client_name", pd.Series())
            .astype(str)
            .str.contains(search_kw, na=False)
        ]

    if filtered_df.empty:
        st.warning("조건에 일치하는 입출고 이력이 없습니다.")
    else:
        st.caption(
            "💡 수량/단가 변경 시 **총금액이 자동 계산**되며, 저장 시 DB 및 재고에 즉시 반영됩니다."
        )

        # 칼럼 순서 정렬
        cols_order = [
            "선택",
            "type",
            "date",
            "item_category",
            "warehouse",
            "client_name",
            "product_name",
            "jan_code",
            "qty",
            "unit_price",
            "total_amount",
            "note",
        ]
        cols_exist = [c for c in cols_order if c in filtered_df.columns]

        # =============================================================================
        # ✏️ 3. 데이터 에디터 (수정/선택 기능)
        # =============================================================================
        edited_df = st.data_editor(
            filtered_df[cols_exist],
            use_container_width=True,
            column_config={
                "선택": st.column_config.CheckboxColumn(
                    "선택", help="삭제할 항목을 체크하세요.", default=False
                ),
                "type": st.column_config.SelectboxColumn(
                    "구분", options=["입고", "출고"], required=True
                ),
                "item_category": st.column_config.SelectboxColumn(
                    "분류", options=["상품", "집기"], required=True
                ),
                "warehouse": st.column_config.SelectboxColumn(
                    "창고", options=existing_whs, required=True
                ),
                "date": st.column_config.TextColumn("일자"),
                "client_name": st.column_config.TextColumn("거래처"),
                "product_name": st.column_config.TextColumn("품목/상품명"),
                "jan_code": st.column_config.TextColumn("JAN 코드"),
                "qty": st.column_config.NumberColumn(
                    "수량 (EA)", min_value=1, step=1, format="%,d"
                ),
                "unit_price": st.column_config.NumberColumn(
                    "단가 (공급가)", min_value=0, format="%,d"
                ),
                "total_amount": st.column_config.NumberColumn(
                    "총 금액", min_value=0, format="%,d", disabled=True
                ),
                "note": st.column_config.TextColumn("비고"),
            },
            key="stock_logs_editor_single_page",
        )

        # =============================================================================
        # 💾 4. 작업 버튼 (저장 / 삭제 / 다운로드)
        # =============================================================================
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2, 2, 2, 2])

        # 1) 변경사항 DB 및 세션에 저장
        with btn_col1:
            if st.button(
                "💾 변경사항 저장", type="primary", use_container_width=True
            ):
                for idx, row in edited_df.iterrows():
                    orig_idx = filtered_df.loc[idx, "_orig_idx"]

                    row_dict = row.drop(
                        ["선택", "_orig_idx"], errors="ignore"
                    ).to_dict()

                    # 수량 * 단가 총액 자동 재계산
                    qty_val = row_dict.get("qty", 0) or 0
                    unit_val = row_dict.get("unit_price", 0) or 0
                    row_dict["total_amount"] = qty_val * unit_val

                    # 세션 업데이트
                    st.session_state.stock_logs[orig_idx].update(row_dict)

                # DB 영구 저장
                db.save_stock_logs_bulk(st.session_state.stock_logs)

                st.success("수정사항이 DB 및 세션에 성공적으로 저장되었습니다!")
                st.rerun()

        # 2) 선택 항목 삭제
        with btn_col2:
            if st.button(
                "🗑️ 선택 항목 삭제", type="secondary", use_container_width=True
            ):
                selected_rows = edited_df[edited_df["선택"] == True]

                if selected_rows.empty:
                    st.warning("삭제할 항목을 먼저 체크해 주세요.")
                else:
                    delete_indices = [
                        filtered_df.loc[r_idx, "_orig_idx"]
                        for r_idx in selected_rows.index
                    ]

                    # 세션 리스트에서 대상 인덱스 제거
                    st.session_state.stock_logs = [
                        log
                        for idx, log in enumerate(st.session_state.stock_logs)
                        if idx not in delete_indices
                    ]

                    # DB 영구 반영
                    db.save_stock_logs_bulk(st.session_state.stock_logs)

                    st.success(
                        f"{len(delete_indices)}건의 이력이 성공적으로 삭제되었습니다."
                    )
                    st.rerun()

        # 다운로드 전용 데이터 정리 (선택/내부 열 제외)
        download_df = edited_df.drop(
            columns=["선택", "_orig_idx"], errors="ignore"
        ).copy()

        # 3) CSV 다운로드 버튼
        with btn_col3:
            csv_data = download_df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📄 CSV 다운로드",
                data=csv_data,
                file_name="입출고이력_조회결과.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # 4) Excel 다운로드 버튼
        with btn_col4:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                download_df.to_excel(
                    writer, index=False, sheet_name="입출고이력"
                )
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📊 Excel 다운로드",
                data=excel_data,
                file_name="입출고이력_조회결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
