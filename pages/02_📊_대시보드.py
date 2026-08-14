import datetime
import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# 1. 언어 딕셔너리 정의
TRANSLATIONS = {
    "KO": {
        "page_title": "대시보드",
        "title": "📊 통합 대시보드 및 매출/출고 분석",
        "no_data": "💡 등록된 입출고 및 매출 이력이 아직 없습니다. 재고관리에서 엑셀 대량 등록 또는 개별 출고를 진행해 주세요.",
        "search_filter": "🔍 통합 검색 및 조건 필터",
        "date_range": "기간 선택",
        "select_client": "거래처 선택",
        "select_product": "상품 선택",
        "select_purpose": "용도 선택",
        "all": "전체",
        "purpose_delivery": "납품",
        "purpose_sample": "샘플",
        "purpose_foc": "FOC",
        "metric_total_sales": "총 유상 매출액 (납품)",
        "metric_commercial_qty": "유상 출고 수량",
        "metric_sample_qty": "무상 출고 수량 (샘플+FOC)",
        "metric_sample_value": "샘플/FOC 환산 가치",
        "unit_pcs": "개",
        "tab1_title": "🛒 용도별(납품/샘플/FOC) 상세",
        "tab2_title": "🏢 거래처별 매출 현황",
        "tab3_title": "📦 상품별 출고 현황",
        "tab1_header": "용도별 (납품 / 샘플 / FOC) 출고 내역",
        "tab2_header": "거래처별 출고 및 매출 집계",
        "tab3_header": "상품별 출고 집계",
        # 컬럼 변환 매핑
        "col_date": "일자",
        "col_order_no": "주문번호",
        "col_client_name": "거래처명",
        "col_product_name": "상품명",
        "col_purpose": "용도",
        "col_qty": "수량",
        "col_unit_price": "단가",
        "col_total_amount": "총금액",
        "col_warehouse": "창고",
        "col_status": "상태",
        "col_jan_code": "JAN 코드",
    },
    "JA": {
        "page_title": "ダッシュボード",
        "title": "📊 統合ダッシュボードおよび売上・出荷分析",
        "no_data": "💡 登録された入出荷および売上履歴がまだありません。在庫管理からエクセル一括登録または個別出荷を行ってください。",
        "search_filter": "🔍 統合検索および条件フィルター",
        "date_range": "期間選択",
        "select_client": "取引先選択",
        "select_product": "商品選択",
        "select_purpose": "用途選択",
        "all": "全体",
        "purpose_delivery": "納품",
        "purpose_sample": "サンプル",
        "purpose_foc": "FOC",
        "metric_total_sales": "総有償売上高 (納品)",
        "metric_commercial_qty": "有償出荷数量",
        "metric_sample_qty": "無償出荷数量 (サンプル+FOC)",
        "metric_sample_value": "サンプル/FOC 換算価値",
        "unit_pcs": "個",
        "tab1_title": "🛒 用途別(納品/サンプル/FOC) 詳細",
        "tab2_title": "🏢 取引先別売上状況",
        "tab3_title": "📦 商品別出荷状況",
        "tab1_header": "用途別 (納品 / サンプル / FOC) 出荷履歴",
        "tab2_header": "取引先別出荷および売上集計",
        "tab3_header": "商品別出荷集計",
        "col_date": "日付",
        "col_order_no": "注文番号",
        "col_client_name": "取引先名",
        "col_product_name": "商品名",
        "col_purpose": "用途",
        "col_qty": "数量",
        "col_unit_price": "単価",
        "col_total_amount": "合計金額",
        "col_warehouse": "倉庫",
        "col_status": "ステータス",
        "col_jan_code": "JANコード",
    },
    "EN": {
        "page_title": "Dashboard",
        "title": "📊 Integrated Dashboard & Sales/Outbound Analysis",
        "no_data": "💡 No stock or sales history found. Please process bulk Excel upload or individual shipment in Inventory Management.",
        "search_filter": "🔍 Search & Filters",
        "date_range": "Select Date Range",
        "select_client": "Select Client",
        "select_product": "Select Product",
        "select_purpose": "Select Purpose",
        "all": "All",
        "purpose_delivery": "Delivery",
        "purpose_sample": "Sample",
        "purpose_foc": "FOC",
        "metric_total_sales": "Total Paid Sales (Delivery)",
        "metric_commercial_qty": "Paid Shipment Qty",
        "metric_sample_qty": "Free Shipment Qty (Sample+FOC)",
        "metric_sample_value": "Sample/FOC Estimated Value",
        "unit_pcs": "pcs",
        "tab1_title": "🛒 Details by Purpose",
        "tab2_title": "🏢 Sales by Client",
        "tab3_title": "📦 Shipments by Product",
        "tab1_header": "Shipment History by Purpose (Delivery / Sample / FOC)",
        "tab2_header": "Shipment & Sales Summary by Client",
        "tab3_header": "Shipment Summary by Product",
        "col_date": "Date",
        "col_order_no": "Order No.",
        "col_client_name": "Client Name",
        "col_product_name": "Product Name",
        "col_purpose": "Purpose",
        "col_qty": "Qty",
        "col_unit_price": "Unit Price",
        "col_total_amount": "Total Amount",
        "col_warehouse": "Warehouse",
        "col_status": "Status",
        "col_jan_code": "JAN Code",
    },
}

# 2. 현재 선택된 언어 감지 ('lang' 키가 없으면 기본값 'KO')
current_lang = st.session_state.get("lang", "KO")
if current_lang not in TRANSLATIONS:
    current_lang = "KO"

t = TRANSLATIONS[current_lang]

# Streamlit 페이지 설정
st.set_page_config(page_title=t["page_title"], layout="wide")

# 사이드바 렌더링
render_sidebar()

st.title(t["title"])
st.markdown("---")

logs = st.session_state.get("stock_logs", [])

if not logs:
    st.info(t["no_data"])
else:
    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["date"])

    # --- 상단 필터 영역 ---
    st.subheader(t["search_filter"])
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        min_date = df["date"].min().date() if not df.empty else datetime.date.today()
        max_date = df["date"].max().date() if not df.empty else datetime.date.today()
        date_range = st.date_input(t["date_range"], [min_date, max_date])

    with f_col2:
        client_options = [t["all"]] + list(df["client_name"].unique()) if "client_name" in df.columns else [t["all"]]
        sel_client = st.selectbox(t["select_client"], client_options)

    with f_col3:
        product_options = [t["all"]] + list(df["product_name"].unique()) if "product_name" in df.columns else [t["all"]]
        sel_product = st.selectbox(t["select_product"], product_options)

    with f_col4:
        purposes = [t["all"], "납품", "샘플", "FOC"]
        sel_purpose = st.selectbox(t["select_purpose"], purposes)

    # 필터링 적용
    filtered_df = df.copy()
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df["date"].dt.date >= date_range[0]) & (filtered_df["date"].dt.date <= date_range[1])
        ]
    if sel_client != t["all"]:
        filtered_df = filtered_df[filtered_df["client_name"] == sel_client]
    if sel_product != t["all"]:
        filtered_df = filtered_df[filtered_df["product_name"] == sel_product]
    if sel_purpose != t["all"]:
        filtered_df = filtered_df[filtered_df["purpose"] == sel_purpose]

    st.markdown("---")

    # --- 핵심 지표 (납품 vs 샘플+FOC 분리) ---
    out_df = filtered_df[filtered_df["type"] == "출고"] if "type" in filtered_df.columns else filtered_df

    commercial_df = out_df[out_df["purpose"] == "납품"] if "purpose" in out_df.columns else pd.DataFrame()
    sample_foc_df = out_df[out_df["purpose"].isin(["샘플", "FOC"])] if "purpose" in out_df.columns else pd.DataFrame()

    total_sales = commercial_df["total_amount"].sum() if not commercial_df.empty else 0
    commercial_qty = commercial_df["qty"].sum() if not commercial_df.empty else 0
    sample_qty = sample_foc_df["qty"].sum() if not sample_foc_df.empty else 0
    sample_value = sample_foc_df["total_amount"].sum() if not sample_foc_df.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(t["metric_total_sales"], f"¥{int(total_sales):,}")
    with m2:
        st.metric(t["metric_commercial_qty"], f"{int(commercial_qty):,} {t['unit_pcs']}")
    with m3:
        st.metric(t["metric_sample_qty"], f"{int(sample_qty):,} {t['unit_pcs']}")
    with m4:
        st.metric(t["metric_sample_value"], f"¥{int(sample_value):,}")

    st.markdown("---")

    # --- 상세 현황 탭 ---
    tab1, tab2, tab3 = st.tabs([t["tab1_title"], t["tab2_title"], t["tab3_title"]])

    # 컬럼 변환용 딕셔너리
    column_rename_map = {
        "date": t["col_date"],
        "order_no": t["col_order_no"],
        "client_name": t["col_client_name"],
        "product_name": t["col_product_name"],
        "purpose": t["col_purpose"],
        "qty": t["col_qty"],
        "unit_price": t["col_unit_price"],
        "total_amount": t["col_total_amount"],
        "warehouse": t["col_warehouse"],
        "status": t["col_status"],
        "jan_code": t["col_jan_code"],
    }

    with tab1:
        st.subheader(t["tab1_header"])
        target_cols = ["date", "order_no", "client_name", "product_name", "purpose", "qty", "unit_price", "total_amount", "warehouse", "status"]
        valid_cols = [c for c in target_cols if c in out_df.columns]
        
        tab1_df = out_df[valid_cols].rename(columns=column_rename_map)
        st.dataframe(tab1_df, use_container_width=True)

    with tab2:
        st.subheader(t["tab2_header"])
        if not out_df.empty and "client_name" in out_df.columns and "purpose" in out_df.columns:
            client_summary = out_df.groupby(["client_name", "purpose"])[["qty", "total_amount"]].sum().reset_index()
            tab2_df = client_summary.rename(columns=column_rename_map)
            st.dataframe(tab2_df, use_container_width=True)

    with tab3:
        st.subheader(t["tab3_header"])
        group_cols = [c for c in ["jan_code", "product_name", "purpose"] if c in out_df.columns]
        if not out_df.empty and group_cols:
            product_summary = out_df.groupby(group_cols)[["qty", "total_amount"]].sum().reset_index()
            tab3_df = product_summary.rename(columns=column_rename_map)
            st.dataframe(tab3_df, use_container_width=True)
