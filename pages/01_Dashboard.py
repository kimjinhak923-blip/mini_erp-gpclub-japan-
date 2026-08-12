import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.db_client import supabase
from utils.auth import require_auth
from utils.i18n import t

st.set_page_config(page_title=t("dashboard_title"), page_icon="📊", layout="wide")
require_auth()

st.title(t("dashboard_title"))

tab_main, tab_detail = st.tabs([f"📈 {t('monthly_summary')}", t("detail_search")])

# -------------------------------------------------------------------
# [탭 1] 월별 매출 개요 & 차트
# -------------------------------------------------------------------
with tab_main:
    col_m1, _ = st.columns([1, 3])
    with col_m1:
        selected_month_str = st.date_input(t("select_month"), value=date.today())
        year = selected_month_str.year
        month = selected_month_str.month

    # 해당 월의 시작일과 종료일 계산
    start_of_month = date(year, month, 1)
    if month == 12:
        end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(year, month + 1, 1) - timedelta(days=1)

    # 납품일(delivery_date) 기준 데이터 조회
    res = supabase.table("sales_orders") \
        .select("*") \
        .gte("delivery_date", start_of_month.isoformat()) \
        .lte("delivery_date", end_of_month.isoformat()) \
        .execute()

    sales_data = res.data if res.data else []

    total_sales = 0
    offline_sales = 0
    online_sales = 0

    if sales_data:
        df_month = pd.DataFrame(sales_data)
        df_month['amount'] = df_month['total_amount'].astype(float)
        
        total_sales = df_month['amount'].sum()
        offline_sales = df_month[df_month['order_type'] == 'OFFLINE']['amount'].sum()
        online_sales = df_month[df_month['order_type'] == 'ONLINE']['amount'].sum()

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric(t("total_sales"), f"₩{total_sales:,.0f}")
    m_col2.metric(t("offline_sales"), f"₩{offline_sales:,.0f}")
    m_col3.metric(t("online_sales"), f"₩{online_sales:,.0f}")

    st.markdown("---")
    st.subheader(f"📅 {year}년 {month}월 {t('sales_trend')}")

    if sales_data:
        # 일별/채널별 피벗 테이블 구성
        df_month['delivery_date'] = pd.to_datetime(df_month['delivery_date'])
        chart_df = df_month.pivot_table(
            index='delivery_date', 
            columns='order_type', 
            values='amount', 
            aggfunc='sum'
        ).fillna(0)

        # 리네임 (그래프 범례)
        chart_df = chart_df.rename(columns={'OFFLINE': '오프라인(납품)', 'ONLINE': '온라인(EC)'})
        st.line_chart(chart_df)
    else:
        st.info("선택한 월에 조회된 매출(납품) 기록이 없습니다.")

# -------------------------------------------------------------------
# [탭 2] 하위 카테고리: 상세 조회 (기간 선택 및 일별 내역)
# -------------------------------------------------------------------
with tab_detail:
    st.subheader(t("detail_search"))
    
    col_p1, col_p2 = st.columns(2)
    default_start = date.today() - timedelta(days=30)
    default_end = date.today()
    
    start_date = col_p1.date_input("시작일", value=default_start)
    end_date = col_p2.date_input("종료일", value=default_end)

    if (end_date - start_date).days > 365:
        st.warning("⚠️ 최대 1년(365일) 이내의 기간만 선택 가능합니다.")
    elif start_date > end_date:
        st.error("시작일은 종료일보다 이전이어야 합니다.")
    else:
        # 납품일(delivery_date) 기준 기간 조회
        detail_res = supabase.table("sales_orders") \
            .select("*") \
            .gte("delivery_date", start_date.isoformat()) \
            .lte("delivery_date", end_date.isoformat()) \
            .order("delivery_date", desc=False) \
            .execute()

        detail_data = detail_res.data if detail_res.data else []

        if detail_data:
            df_detail = pd.DataFrame(detail_data)
            df_detail['amount'] = df_detail['total_amount'].astype(float)

            tot_sum = df_detail['amount'].sum()
            off_sum = df_detail[df_detail['order_type'] == 'OFFLINE']['amount'].sum()
            on_sum = df_detail[df_detail['order_type'] == 'ONLINE']['amount'].sum()

            c1, c2, c3 = st.columns(3)
            c1.metric(f"기간 총합 매출 ({start_date} ~ {end_date})", f"₩{tot_sum:,.0f}")
            c2.metric("오프라인(납품) 합계", f"₩{off_sum:,.0f}")
            c3.metric("온라인(EC) 합계", f"₩{on_sum:,.0f}")

            st.markdown("---")
            st.markdown(f"##### 📋 {t('daily_breakdown')}")

            # 일별 집계 표
            daily_summary = df_detail.groupby(['delivery_date', 'order_type'])['amount'].sum().unstack(fill_value=0).reset_index()
            if 'OFFLINE' not in daily_summary.columns: daily_summary['OFFLINE'] = 0
            if 'ONLINE' not in daily_summary.columns: daily_summary['ONLINE'] = 0

            daily_summary['일별 총매출'] = daily_summary['OFFLINE'] + daily_summary['ONLINE']
            daily_summary = daily_summary.rename(columns={
                'delivery_date': '납품일자',
                'OFFLINE': '오프라인 매출',
                'ONLINE': '온라인 매출'
            })

            st.dataframe(daily_summary, use_container_width=True, hide_index=True)
        else:
            st.info("해당 기간 내 납품 완료된 매출 데이터가 없습니다.")
