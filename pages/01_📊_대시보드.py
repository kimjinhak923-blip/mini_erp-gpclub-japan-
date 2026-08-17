import datetime
import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar

st.set_page_config(page_title="대시보드", layout="wide")
render_sidebar()

# DB 테이블 초기화
db.init_db()

# --- 데이터베이스 및 세션 상태 자동 연동 ---
if "stock_logs" not in st.session_state:
    st.session_state.stock_logs = (
        db.get_stock_logs() if hasattr(db, "get_stock_logs") else []
    )
if "products" not in st.session_state:
    st.session_state.products = (
        db.get_products() if hasattr(db, "get_products") else []
    )
if "clients" not in st.session_state:
    st.session_state.clients = (
        db.get_clients() if hasattr(db, "get_clients") else []
    )
if "warehouses" not in st.session_state:
    st.session_state.warehouses = (
        db.get_warehouses() if hasattr(db, "get_warehouses") else []
    )

st.title("📊 통합 대시보드 및 매출/출고 분석")
st.markdown("---")

logs = st.session_state.get("stock_logs", [])

if not logs:
    st.info(
        "💡 등록된 입출고 및 매출 이력이 아직 없습니다. 재고관리에서 엑셀 대량 등록 또는 개별 출고를 진행해 주세요."
    )
else:
    df = pd.DataFrame(logs)

    # --- 데이터 연동 및 타입 안정성 보장 ---
    required_cols = {
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "type": "출고",
        "item_category": "제품",
        "purpose": "납품",
        "product_name": "",
        "jan_code": "",
        "qty": 0,
        "total_amount": 0,
        "warehouse": "",
        "client_name": "",
    }
    for col, default_val in required_cols.items():
        if col not in df.columns:
            df[col] = default_val

    # 날짜 및 수치형 변환 (문자열 포함 대비)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0)
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
    df["client_name"] = df["client_name"].fillna("").astype(str)
    df["product_name"] = df["product_name"].fillna("").astype(str)
    df["purpose"] = df["purpose"].fillna("").astype(str)
    df["jan_code"] = df["jan_code"].fillna("").astype(str)
    df["warehouse"] = df["warehouse"].fillna("").astype(str)

    # --- 상단 필터 영역 ---
    st.subheader("🔍 통합 검색 및 조건 필터")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    valid_dates = df["date"].dropna()
    with f_col1:
        min_date = (
            valid_dates.min().date() if not valid_dates.empty else datetime.date.today()
        )
        max_date = (
            valid_dates.max().date() if not valid_dates.empty else datetime.date.today()
        )
        date_range = st.date_input("기간 선택", [min_date, max_date])

    with f_col2:
        clients = ["전체"] + sorted([c for c in df["client_name"].unique() if c])
        sel_client = st.selectbox("거래처 선택", clients)

    with f_col3:
        products = ["전체"] + sorted([p for p in df["product_name"].unique() if p])
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

    # --- 상세 현황 탭 ---
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

        total_out_qty = int(out_df["qty"].sum())
        total_out_amount = int(out_df["total_amount"].sum())

        sum_c1, sum_c2 = st.columns(2)
        sum_c1.info(f"📌 **조회 기간 내 총 출고량:** `{total_out_qty:,}` 개")
        sum_c2.success(
            f"💰 **조회 기간 내 총 발주금액합계:** `¥{total_out_amount:,}`"
        )

        if not out_df.empty:
            grouped_tab1 = (
                out_df.groupby(["jan_code", "product_name", "purpose"])[
                    ["qty", "total_amount"]
                ]
                .sum()
                .reset_index()
            )

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
    # TAB 2: 거래처별 조회 (JAN코드/상품명/용도별 자동 합산)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("🏢 거래처별 출고 및 발주 합산 조회")

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

        all_client_options = sorted(
            list(set(registered_clients + history_clients))
        )

        if not all_client_options:
            st.info("등록되거나 출고된 거래처 내역이 없습니다.")
        else:
            selected_target_client = st.selectbox(
                "🔍 조회할 거래처를 선택하세요",
                options=all_client_options,
                key="tab2_client_select",
            )

            if selected_target_client:
                client_df = out_df[
                    out_df["client_name"] == selected_target_client
                ].copy()

                if not client_df.empty:
                    grouped_client = (
                        client_df.groupby(["jan_code", "product_name", "purpose"])[
                            ["qty", "total_amount"]
                        ]
                        .sum()
                        .reset_index()
                    )

                    c_qty = int(grouped_client["qty"].sum())
                    c_amt = int(grouped_client["total_amount"].sum())

                    st.markdown(
                        f"**[{selected_target_client}]** 검색 조건 합계: **총 {c_qty:,}개** / **총 발주금액 ¥{c_amt:,}**"
                    )

                    def format_client_amount(row):
                        if row["purpose"] == "FOC":
                            return "FOC (¥0)"
                        elif row["purpose"] == "샘플":
                            return "샘플 (¥0)"
                        else:
                            return f"¥{int(row['total_amount']):,}"

                    grouped_client["총 발주금액"] = grouped_client.apply(
                        format_client_amount, axis=1
                    )
                    grouped_client["총 출고수량"] = grouped_client[
                        "qty"
                    ].apply(lambda x: f"{int(x):,} 개")

                    show_client_df = (
                        grouped_client[
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

                    st.dataframe(show_client_df, use_container_width=True)
                else:
                    st.info(
                        f"'{selected_target_client}' 거래처의 조건에 부합하는 출고 내역이 없습니다."
                    )

    # -------------------------------------------------------------------------
    # TAB 3: 상품별 출고 현황
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
    # TAB 4: 창고별 재고 및 재고 평가액
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("🏭 창고별 실시간 재고량 및 재고 평가액")

        default_warehouses = ["SAGAWA", "L&K", "大吉商事"]
        registered_wh = st.session_state.get(
            "warehouses", default_warehouses
        )
        if not registered_wh:
            registered_wh = default_warehouses

        product_master = st.session_state.get("products", [])
        cost_map = {}
        for p in product_master:
            if isinstance(p, dict):
                code = p.get("jan_code") or p.get("product_code")
                if code:
                    try:
                        cost_map[str(code)] = float(
                            p.get("cost_price", p.get("purchase_price", 0))
                        )
                    except (ValueError, TypeError):
                        cost_map[str(code)] = 0.0

        all_logs_df = df.copy()

        if sel_product != "전체":
            all_logs_df = all_logs_df[
                all_logs_df["product_name"] == sel_product
            ]

        if not all_logs_df.empty:
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

            for wh in registered_wh:
                st.markdown(f"#### 📦 [{wh}] 창고 재고 현황")
                wh_stock = stock_summary[
                    stock_summary["warehouse"] == wh
                ].copy()

                if not wh_stock.empty:
                    wh_stock["cost_price"] = wh_stock["jan_code"].map(
                        lambda c: cost_map.get(str(c), 0.0)
                    )
                    wh_stock["stock_value"] = (
                        wh_stock["calc_qty"] * wh_stock["cost_price"]
                    )

                    total_wh_qty = int(wh_stock["calc_qty"].sum())
                    total_wh_val = int(wh_stock["stock_value"].sum())

                    st.caption(
                        f"보유 수량: **{total_wh_qty:,}개** | 재고 평가액합계: **¥{total_wh_val:,}**"
                    )

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
