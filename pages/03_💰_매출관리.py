import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# 1. 언어별 번역 딕셔너리 정의 (한국어/일본어/영어)
TRANSLATIONS = {
    "KO": {
        "page_title": "매출관리",
        "title": "💰 매출 현황 및 분석",
        "no_data": "매출(출고) 내역이 아직 없습니다.",
        "metric_total_rev": "총 매출액 (JPY)",
        "metric_total_qty": "총 출고 수량",
        "unit_pcs": "개",
        "header_client_summary": "🏢 거래처별 매출 합계",
        "header_prod_summary": "📦 상품별 매출 합계",
        # 컬럼명 매핑
        "col_client_name": "거래처명",
        "col_jan_code": "JAN 코드",
        "col_product_name": "상품명",
        "col_qty": "수량",
        "col_total_amount": "총금액",
    },
    "JA": {
        "page_title": "売上管理",
        "title": "💰 売上状況および分析",
        "no_data": "売上(出荷)履歴がまだありません。",
        "metric_total_rev": "総売上高 (JPY)",
        "metric_total_qty": "総出荷数量",
        "unit_pcs": "個",
        "header_client_summary": "🏢 取引先別売上合計",
        "header_prod_summary": "📦 商品別売上合計",
        "col_client_name": "取引先名",
        "col_jan_code": "JANコード",
        "col_product_name": "商品名",
        "col_qty": "数量",
        "col_total_amount": "合計金額",
    },
    "EN": {
        "page_title": "Sales Management",
        "title": "💰 Sales Status & Analysis",
        "no_data": "No sales (outbound) history found.",
        "metric_total_rev": "Total Revenue (JPY)",
        "metric_total_qty": "Total Outbound Qty",
        "unit_pcs": "pcs",
        "header_client_summary": "🏢 Revenue by Client",
        "header_prod_summary": "📦 Revenue by Product",
        "col_client_name": "Client Name",
        "col_jan_code": "JAN Code",
        "col_product_name": "Product Name",
        "col_qty": "Qty",
        "col_total_amount": "Total Amount",
    },
}

# 2. 현재 선택된 언어 감지 ('lang' 또는 'language' 세션 키 참조)
current_lang = st.session_state.get("lang") or st.session_state.get("language") or "KO"
if current_lang not in TRANSLATIONS:
    current_lang = "KO"

t = TRANSLATIONS[current_lang]

# 3. Streamlit 페이지 설정 (반드시 최상단 실행)
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 렌더링 및 사용자 정보 확인
render_sidebar()
user = st.session_state.get("logged_in_user")

# 5. 본문 영역
st.title(t["title"])
st.markdown("---")

out_logs = [log for log in st.session_state.get("stock_logs", []) if log.get("type") == "출고"]

if not out_logs:
    st.info(t["no_data"])
else:
    df_sales = pd.DataFrame(out_logs)

    # 데이터 타입 변환 및 예외 처리
    for col in ["total_amount", "qty"]:
        if col in df_sales.columns:
            df_sales[col] = pd.to_numeric(df_sales[col], errors="coerce").fillna(0)
        else:
            df_sales[col] = 0

    total_rev = int(df_sales["total_amount"].sum())
    total_qty = int(df_sales["qty"].sum())

    c1, c2 = st.columns(2)
    with c1:
        st.metric(t["metric_total_rev"], f"¥{total_rev:,}")
    with c2:
        st.metric(t["metric_total_qty"], f"{total_qty:,} {t['unit_pcs']}")

    st.markdown("---")
    st.subheader(t["header_client_summary"])
    
    if "client_name" in df_sales.columns:
        cli_summary = (
            df_sales.groupby("client_name")[["qty", "total_amount"]]
            .sum()
            .reset_index()
        )
        # 컬럼명 언어에 맞게 재정의
        cli_summary_renamed = cli_summary.rename(
            columns={
                "client_name": t["col_client_name"],
                "qty": t["col_qty"],
                "total_amount": t["col_total_amount"],
            }
        )
        st.dataframe(cli_summary_renamed, use_container_width=True)

    st.markdown("---")
    st.subheader(t["header_prod_summary"])
    
    group_prod_cols = [c for c in ["jan_code", "product_name"] if c in df_sales.columns]
    if group_prod_cols:
        prod_summary = (
            df_sales.groupby(group_prod_cols)[["qty", "total_amount"]]
            .sum()
            .reset_index()
        )
        # 컬럼명 언어에 맞게 재정의
        prod_summary_renamed = prod_summary.rename(
            columns={
                "jan_code": t["col_jan_code"],
                "product_name": t["col_product_name"],
                "qty": t["col_qty"],
                "total_amount": t["col_total_amount"],
            }
        )
        st.dataframe(prod_summary_renamed, use_container_width=True)
