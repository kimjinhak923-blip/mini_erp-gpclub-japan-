import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t, render_sidebar

st.set_page_config(page_title=t("dashboard_title"), page_icon="📊", layout="wide")
require_auth()
render_sidebar()

st.title(t("dashboard_title"))

tab_monthly, tab_detail = st.tabs([t("tab_monthly"), t("tab_detail")])

# -------------------------------------------------------------------
# [탭 1] 월별 조회 (연도 및 월만 선택)
# -------------------------------------------------------------------
with tab_monthly:
    col_y, col_m = st.columns(2)
    current_year = date.today().year
    
    selected_year = col_y.selectbox(t("select_year"), range(current_year - 3, current_year + 2), index=3)
    selected_month = col_m.selectbox(t("select_month"), range(1, 13), index=date.today().month - 1)

    start_date = date(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = date(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(selected_year, selected_month + 1, 1) - timedelta(days=1)

    res = supabase.table("sales_orders") \
        .select("*, sales_order_items(*, products(*))") \
        .gte("delivery_date", start_date.isoformat()) \
        .lte("delivery_date", end_date.isoformat()) \
        .execute()

    sales = res.data or []
    tot_jpy = sum(f["total_amount_jpy"] for f in sales)
    tot_qty = sum(f["total_qty"] for f in sales)

    m1, m2 = st.columns(2)
    m1.metric(f"📅 {selected_year}-{selected_month:02d} 총 매출액 (JPY, VAT별도)", f"¥{tot_jpy:,.0f}")
    m2.metric(f"📦 총 출고 수량", f"{tot_qty:,} 개")

# -------------------------------------------------------------------
# [탭 2] 상세 기간 조회 (1일, 1주일, 1달, 1년, 직접 지정 프셋)
# -------------------------------------------------------------------
with tab_detail:
    st.subheader(t("tab_detail"))
    preset = st.radio(t("preset_select"), [t("preset_1d"), t("preset_1w"), t("preset_1m"), t("preset_1y"), t("preset_custom")], horizontal=True)

    today = date.today()
    if preset == t("preset_1d"):
        d_start, d_end = today, today
    elif preset == t("preset_1w"):
        d_start, d_end = today - timedelta(days=7), today
    elif preset == t("preset_1m"):
        d_start, d_end = today - timedelta(days=30), today
    elif preset == t("preset_1y"):
        d_start, d_end = today - timedelta(days=365), today
    else:
        c1, c2 = st.columns(2)
        d_start = c1.date_input("시작일", value=today - timedelta(days=30))
        d_end = c2.date_input("종료일", value=today)

    detail_res = supabase.table("sales_orders") \
        .select("order_no, delivery_date, delivery_name, total_qty, total_amount_jpy, warehouses(name), partners(name)") \
        .gte("delivery_date", d_start.isoformat()) \
        .lte("delivery_date", d_end.isoformat()) \
        .execute()

    if detail_res.data:
        df_detail = pd.DataFrame(detail_res.data)
        st.dataframe(df_detail, use_container_width=True)
    else:
        st.info("해당 기간의 출고/납품 데이터가 없습니다.")
