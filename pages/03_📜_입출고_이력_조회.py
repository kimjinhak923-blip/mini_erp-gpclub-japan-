import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

st.set_page_config(page_title="입출고 이력 조회 및 수정", layout="wide")
render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("📜 입출고 통합 이력 조회 및 관리")
st.markdown("---")

# 세션 상태 내역 확인
if "stock_logs" not in st.session_state or not st.session_state.stock_logs:
    st.info("입출고 이력이 존재하지 않습니다.")
else:
    # 원본 데이터 로드
    df_logs = pd.DataFrame(st.session_state.stock_logs)

    # 원본 세션 내역과의 인덱스 매핑을 위해 고유 ID/인덱스 부여
    df_logs["_orig_idx"] = df_logs.index
    df_logs["선택"] = False

    # 필터 옵션용 기본 창고 목록 가져오기
    warehouses_list = st.session_state.get(
        "warehouses", ["SAGAWA", "L&K", "大吉商事"]
    )

    # -----------------------------------------------------------------------------
    # 🔍 필터 영역
    # -----------------------------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    with c1:
        type_filter = st.multiselect(
            "구분 필터", ["입고", "출고"], default=["입고", "출고"]
        )
    with c2:
        # 창고 필터 (기존 창고 목록 + 데이터에만 존재하는 창고 병합)
        existing_whs = list(
            set(warehouses_list + df_logs.get("warehouse", pd.Series()).tolist())
        )
        wh_filter = st.multiselect(
            "창고 필터",
            existing_whs,
            default=existing_whs,
        )
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
            "💡 표에서 직접 항목을 수정하거나, 삭제할 항목의 '선택'란에 체크 후 하단 버튼을 클릭하세요."
        )

        # 칼럼 순서 정렬 ("선택" 열을 최좌측으로 배치)
        cols_order = ["선택"] + [
            c for c in filtered_df.columns if c not in ["선택", "_orig_idx"]
        ]
        filtered_df_display = filtered_df[cols_order]

        # -----------------------------------------------------------------------------
        # ✏️ 데이터 에디터 (수정 및 선택 삭제 가능)
        # -----------------------------------------------------------------------------
        edited_df = st.data_editor(
            filtered_df_display,
            use_container_width=True,
            column_config={
                "선택": st.column_config.CheckboxColumn(
                    "선택", help="삭제할 이력을 체크하세요.", default=False
                ),
                "type": st.column_config.SelectboxColumn(
                    "구분", options=["입고", "출고"], required=True
                ),
                "qty": st.column_config.NumberColumn(
                    "수량", min_value=1, step=1, format="%d EA"
                ),
                "warehouse": st.column_config.SelectboxColumn(
                    "창고", options=existing_whs
                ),
            },
            key="stock_logs_editor",
        )

        # -----------------------------------------------------------------------------
        # 💾 작업 버튼 (수정 저장 / 선택 삭제)
        # -----------------------------------------------------------------------------
        btn_col1, btn_col2, _ = st.columns([2, 2, 6])

        # 1. 수정사항 저장
        with btn_col1:
            if st.button("💾 변경사항 저장", type="primary", use_container_width=True):
                # 편집된 데이터를 원본 세션에 반영
                for _, row in edited_df.iterrows():
                    orig_idx = filtered_df.loc[row.name, "_orig_idx"]
                    
                    # '선택' 및 내부 매핑 키 제외 후 세션 업데이트
                    row_data = row.drop(["선택"], errors="ignore").to_dict()
                    
                    # 기존 세션 데이터 구조 유지하며 갱신
                    st.session_state.stock_logs[orig_idx].update(row_data)

                st.success("입출고 이력 수정사항이 성공적으로 저장되었습니다!")
                st.rerun()

        # 2. 선택 항목 삭제
        with btn_col2:
            if st.button("🗑️ 선택 항목 삭제", type="secondary", use_container_width=True):
                selected_rows = edited_df[edited_df["선택"] == True]

                if selected_rows.empty:
                    st.warning("삭제할 항목을 먼저 체크해 주세요.")
                else:
                    # 삭제 대상 원본 인덱스 추출
                    delete_indices = [
                        filtered_df.loc[r_idx, "_orig_idx"]
                        for r_idx in selected_rows.index
                    ]

                    # 세션 리스트에서 대상 인덱스 차감 및 재구성
                    st.session_state.stock_logs = [
                        log
                        for idx, log in enumerate(st.session_state.stock_logs)
                        if idx not in delete_indices
                    ]

                    st.success(
                        f"선택한 {len(delete_indices)}건의 이력이 삭제되었습니다."
                    )
                    st.rerun()
