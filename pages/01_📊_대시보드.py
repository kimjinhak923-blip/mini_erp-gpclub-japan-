import datetime
import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

st.set_page_config(page_title="대시보드", layout="wide")
render_sidebar()

st.title("📊 통합 대시보드 및 매출/출고 분석")
st.markdown("---")

logs = st.session_state.get("stock_logs", [])

if not logs:
    st.info(
        "💡 등록된 입출고 및 매출 이력이 아직 없습니다. 재고관리에서 엑셀 대량 등록 또는 개별 출고를 진행해 주세요."
    )
else:
    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["date"])

    # --- 상단 필터 영역 ---
    st.subheader("🔍 통합 검색 및 조건 필터")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        min_date = (
            df["date"].min().date() if not df.empty else datetime.date.today()
        )
        max_date = (
            df["date"].max().date() if not df.empty else datetime.date.today()
        )
        date_range = st.date_input("기간 선택", [min_date, max_date])

    with f_col2:
        clients = ["전체"] + list(df["client_name"].unique())
        sel_client = st.selectbox("거래처 선택", clients)

    with f_col3:
        products = ["전체"] + list(df["product_name"].unique())
        sel_product = st.selectbox("상품 선택", products)

    with f_col4:
        purposes = ["전체", "납품", "샘플", "FOC"]
        sel_purpose = st.selectbox("용도 선택", purposes)

    # 필터링 적용
    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df["date"].dt.date >= date_range[0])
            & (filtered_df["date"].dt.date <= date_range[1])
        ]
    if sel_client != "전체":
        filtered_df = filtered_df[filtered_df["client_name"] == sel_client]
    if sel_product != "전체":
        filtered_df = filtered_df[filtered_df["product_name"] == sel_product]
    if sel_purpose != "전체":
        filtered_df = filtered_df[filtered_df["purpose"] == sel_purpose]

    st.markdown("---")

    # --- 핵심 지표 (납품 vs 샘플+FOC 분리) ---
    out_df = filtered_df[filtered_df["type"] == "출고"].copy()

    commercial_df = out_df[out_df["purpose"] == "납품"]
    sample_foc_df = out_df[out_df["purpose"].isin(["샘플", "FOC"])]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            "총 유상 매출액 (납품)",
            f"¥{int(commercial_df['total_amount'].sum()):,}",
        )
    with m2:
        st.metric("유상 출고 수량", f"{int(commercial_df['qty'].sum()):,} 개")
    with m3:
        st.metric(
            "무상 출고 수량 (샘플+FOC)", f"{int(sample_foc_df['qty'].sum()):,} 개"
        )
    with m4:
        st.metric(
            "샘플/FOC 환산 가치",
            f"¥{int(sample_foc_df['total_amount'].sum()):,}",
        )

    st.markdown("---")

    # --- 상세 현황 탭 (요청사항 반영) ---
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🛒 전체 출고 내역 및 통합 집계",
            "🏢 거래처별 상세 조회",
            "📦 상품별 출고 현황",
            "🏭 창고별 재고 및 평가액",
        ]
    )

# -------------------------------------------------------------------------
    # TAB 1: 전체 출고 내역 및 통합 집계 (JAN코드/상품명/용도별 자동 합산)
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("전체 출고 내역 및 통합 집계")

        # 검색조건 기준 전체 총 출고량 및 발주금액
        total_out_qty = int(out_df["qty"].sum())
        total_out_amount = int(out_df["total_amount"].sum())

        sum_c1, sum_c2 = st.columns(2)
        sum_c1.info(f"📌 **조회 기간 내 총 출고량:** `{total_out_qty:,}` 개")
        sum_c2.success(
            f"💰 **조회 기간 내 총 발주금액합계:** `¥{total_out_amount:,}`"
        )

        if not out_df.empty:
            # 1. JAN코드, 상품명, 용도 기준으로 수량 및 금액 자동 합산
            grouped_tab1 = (
                out_df.groupby(["jan_code", "product_name", "purpose"])[
                    ["qty", "total_amount"]
                ]
                .sum()
                .reset_index()
            )

            # 2. 용도별 금액 표기 분기 처리 (FOC / 샘플 / 유상 납품)
            def format_grouped_amount(row):
                if row["purpose"] == "FOC":
                    return "FOC (¥0)"
                elif row["purpose"] == "샘플":
                    return "샘플 (¥0)"
                else:
                    return f"¥{int(row['total_amount']):,}"

            grouped_tab1["총 발주금액"] = grouped_tab1.apply(
                format_grouped_amount, axis=1
            )
            grouped_tab1["총 출고수량"] = grouped_tab1["qty"].apply(
                lambda x: f"{int(x):,} 개"
            )

            # 3. 테이블 출력 컬럼 정리 및 정렬
            show_tab1 = (
                grouped_tab1[
                    [
                        "jan_code",
                        "product_name",
                        "purpose",
                        "총 출고수량",
                        "총 발주금액",
                    ]
                ]
                .rename(
                    columns={
                        "jan_code": "JAN코드",
                        "product_name": "상품명",
                        "purpose": "용도",
                    }
                )
                .sort_values(by=["JAN코드", "용도"])
            )

            st.dataframe(show_tab1, use_container_width=True)
        else:
            st.warning("조건에 해당하는 출고 데이터가 없습니다.")
            
    # -------------------------------------------------------------------------
    # TAB 2: 거래처별 상세 조회 (드롭다운 선택 및 필터 맞춤 제품 출력)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("거래처별 출고 제품 상세 조회")

        # 1. 거래처 관리 데이터 및 출고 이력 거래처 추출 (None 및 비문자열 안전 제거)
        registered_clients = [
            str(c.get("name")).strip()
            for c in st.session_state.get("clients", [])
            if isinstance(c, dict) and c.get("name")
        ]

        history_clients = [
            str(name).strip()
            for name in out_df["client_name"].unique()
            if pd.notna(name) and str(name).strip() != ""
        ]

        # 2. 중복 제거 및 문자열 정렬 (TypeError 방지 안전 처리)
        all_client_options = sorted(
            list(set(registered_clients + history_clients))
        )

        # 거래처 선택 드롭다운
        if not all_client_options:
            st.info("등록되거나 출고된 거래처 내역이 없습니다.")
        else:
            selected_target_client = st.selectbox(
                "🔍 조회할 거래처를 선택하세요",
                options=all_client_options,
                key="tab2_client_select",
            )

            if selected_target_client:
                client_filtered_df = out_df[
                    out_df["client_name"] == selected_target_client
                ].copy()

                if not client_filtered_df.empty:
                    client_filtered_df["date"] = client_filtered_df[
                        "date"
                    ].dt.strftime("%Y-%m-%d")
                    client_filtered_df["qty_fmt"] = client_filtered_df[
                        "qty"
                    ].apply(lambda x: f"{int(x):,}")
                    client_filtered_df["unit_price_fmt"] = client_filtered_df[
                        "unit_price"
                    ].apply(lambda x: f"¥{int(x):,}")
                    client_filtered_df["total_amount_fmt"] = (
                        client_filtered_df["total_amount"].apply(
                            lambda x: f"¥{int(x):,}"
                        )
                    )

                    # 요약 수치
                    c_qty = int(client_filtered_df["qty"].sum())
                    c_amt = int(client_filtered_df["total_amount"].sum())

                    st.markdown(
                        f"**[{selected_target_client}]** 검색 조건 합계: **총 {c_qty:,}개** / **총 발주금액 ¥{c_amt:,}**"
                    )

                    show_client_df = client_filtered_df[
                        [
                            "date",
                            "order_no",
                            "jan_code",
                            "product_name",
                            "purpose",
                            "qty_fmt",
                            "unit_price_fmt",
                            "total_amount_fmt",
                            "warehouse",
                        ]
                    ].rename(
                        columns={
                            "date": "일자",
                            "order_no": "발주코드",
                            "jan_code": "JAN코드",
                            "product_name": "상품명",
                            "purpose": "용도",
                            "qty_fmt": "수량",
                            "unit_price_fmt": "단가",
                            "total_amount_fmt": "발주금액",
                            "warehouse": "창고",
                        }
                    )
                    st.dataframe(show_client_df, use_container_width=True)
                else:
                    st.info(
                        f"'{selected_target_client}' 거래처의 조건에 부합하는 출고 내역이 없습니다."
                    )

    # -------------------------------------------------------------------------
    # TAB 3: 상품별 출고 현황 (기존 기능 유지 및 포맷팅)
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("상품별 출고 및 매출 집계")
        if not out_df.empty:
            product_summary = (
                out_df.groupby(["jan_code", "product_name", "purpose"])[
                    ["qty", "total_amount"]
                ]
                .sum()
                .reset_index()
            )
            product_summary["qty"] = product_summary["qty"].apply(
                lambda x: f"{int(x):,}"
            )
            product_summary["total_amount"] = product_summary[
                "total_amount"
            ].apply(lambda x: f"¥{int(x):,}")

            product_summary = product_summary.rename(
                columns={
                    "jan_code": "JAN코드",
                    "product_name": "상품명",
                    "purpose": "용도",
                    "qty": "총 출고수량",
                    "total_amount": "총 매출액",
                }
            )
            st.dataframe(product_summary, use_container_width=True)
        else:
            st.info("출고 내역이 없습니다.")

    # -------------------------------------------------------------------------
    # TAB 4: 창고별 재고 및 재고 평가액 (신규 - 시스템 관리 창고 자동 연동)
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("🏭 창고별 실시간 재고량 및 재고 평가액")

        # 1. 시스템 관리에서 등록된 창고 목록 가져오기 (기본값 설정)
        default_warehouses = ["SAGAWA", "L&K", "大吉商事"]
        registered_wh = st.session_state.get(
            "warehouses", default_warehouses
        )
        if not registered_wh:
            registered_wh = default_warehouses

        # 2. 상품 마스터에서 매입 단가(cost_price) 가져오기
        product_master = st.session_state.get("products", [])
        cost_map = {}
        for p in product_master:
            code = p.get("jan_code") or p.get("product_code")
            if code:
                try:
                    cost_map[code] = float(
                        p.get("cost_price", p.get("purchase_price", 0))
                    )
                except (ValueError, TypeError):
                    cost_map[code] = 0.0

        # 3. 입출고 이력(df)을 기반으로 창고별/상품별 재고 자동 계산
        # 전체 이력을 기준으로 창고별 재고 계산 (필터링된 범위 내 상품 기준)
        all_logs_df = pd.DataFrame(logs)

        # 상품 및 검색어 필터 조건 적용 (필터에 맞는 상품만 보기)
        if sel_product != "전체":
            all_logs_df = all_logs_df[
                all_logs_df["product_name"] == sel_product
            ]

        if not all_logs_df.empty:
            # 입고는 (+), 출고는 (-)
            all_logs_df["calc_qty"] = all_logs_df.apply(
                lambda r: r["qty"] if r["type"] == "입고" else -r["qty"],
                axis=1,
            )

            stock_summary = (
                all_logs_df.groupby(["warehouse", "jan_code", "product_name"])[
                    "calc_qty"
                ]
                .sum()
                .reset_index()
            )

            # 창고별 탭 구별 또는 창고별 섹션 표시
            for wh in registered_wh:
                st.markdown(f"#### 📦 [{wh}] 창고 재고 현황")
                wh_stock = stock_summary[
                    stock_summary["warehouse"] == wh
                ].copy()

                if not wh_stock.empty:
                    # 매입단가 및 재고 금액 계산
                    wh_stock["cost_price"] = wh_stock["jan_code"].map(
                        lambda c: cost_map.get(c, 0)
                    )
                    wh_stock["stock_value"] = (
                        wh_stock["calc_qty"] * wh_stock["cost_price"]
                    )

                    # 요약 합계
                    total_wh_qty = int(wh_stock["calc_qty"].sum())
                    total_wh_val = int(wh_stock["stock_value"].sum())

                    st.caption(
                        f"보유 수량: **{total_wh_qty:,}개** | 재고 평가액합계: **¥{total_wh_val:,}**"
                    )

                    # 포맷팅
                    wh_stock["calc_qty"] = wh_stock["calc_qty"].apply(
                        lambda x: f"{int(x):,}"
                    )
                    wh_stock["cost_price"] = wh_stock["cost_price"].apply(
                        lambda x: f"¥{int(x):,}"
                    )
                    wh_stock["stock_value"] = wh_stock["stock_value"].apply(
                        lambda x: f"¥{int(x):,}"
                    )

                    show_wh_df = wh_stock[
                        [
                            "jan_code",
                            "product_name",
                            "calc_qty",
                            "cost_price",
                            "stock_value",
                        ]
                    ].rename(
                        columns={
                            "jan_code": "JAN코드",
                            "product_name": "상품명",
                            "calc_qty": "재고 보유량",
                            "cost_price": "매입 단가",
                            "stock_value": "재고 금액",
                        }
                    )

                    st.dataframe(show_wh_df, use_container_width=True)
                else:
                    st.text(f"[{wh}] 창고에 등록된 재고 데이터가 없습니다.")

                st.markdown("---")
        else:
            st.info("입출고 이력이 존재하지 않습니다.")
