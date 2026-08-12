import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="매출 관리", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

st.header("💰 매출 관리 (납품일/출고건 기준)")

sf1, sf2, sf3, sf4 = st.columns([2, 2, 3, 3])
s_filter_c = sf1.selectbox("거래처 선택 ", ["전체"] + [c["name"] for c in st.session_state.clients])
s_filter_wh = sf2.selectbox("창고 선택 ", ["전체"] + st.session_state.warehouses)
s_start_d = sf3.date_input("시작일 ", datetime.date.today() - datetime.timedelta(days=30))
s_end_d = sf3.date_input("종료일 ", datetime.date.today())
s_kw = sf4.text_input("검색어 (상품명 / 바코드 / 발주번호) ")

sales_data = []
for l in st.session_state.stock_logs:
    if l["type"] != "출고":
        continue
    l_date = datetime.datetime.strptime(l["date"], "%Y-%m-%d").date()
    if not (s_start_d <= l_date <= s_end_d):
        continue
    if s_filter_c != "전체" and l["client"] != s_filter_c:
        continue
    if s_filter_wh != "전체" and l["wh"] != s_filter_wh:
        continue
    if s_kw:
        kw = s_kw.lower()
        if (kw not in l["prod_name"].lower() and 
            kw not in l.get("jan", "").lower() and 
            kw not in l.get("po_no", "").lower()):
            continue

    sales_data.append({
        "발주번호": l.get("po_no", "-"),
        "납품일(출고일)": l["date"],
        "거래처명": l["client"],
        "출고창고": l["wh"],
        "제품명": l["prod_name"],
        "JAN/바코드": l.get("jan", "-"),
        "발주량(수량)": l["qty"],
        "공급가(엔 VAT-)": l["unit_price"],
        "총매출액(공급가*발주량)": l["total_price"],
        "거래방식": l["trade_type"],
    })

st.markdown("---")
total_sales_sum = sum(item["총매출액(공급가*발주량)"] for item in sales_data)
st.metric("📊 조회 기간 총 매출액", f"¥ {total_sales_sum:,}")

if sales_data:
    st.dataframe(pd.DataFrame(sales_data), use_container_width=True)
else:
    st.info("조건에 부합하는 매출 데이터가 없습니다.")
