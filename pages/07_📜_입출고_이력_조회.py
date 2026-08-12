import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="입출고 이력 조회", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

st.header("📜 입출고 이력 통합 조회")

f1, f2, f3, f4 = st.columns([2, 2, 3, 3])
filter_c = f1.selectbox("거래처 선택", ["전체"] + [c["name"] for c in st.session_state.clients])
filter_wh = f2.selectbox("창고 선택", ["전체"] + st.session_state.warehouses)
start_d = f3.date_input("시작일", datetime.date.today() - datetime.timedelta(days=30))
end_d = f3.date_input("종료일", datetime.date.today())
search_kw = f4.text_input("검색어 (상품명 / 바코드 / 발주번호)")

filtered_logs = []
for l in st.session_state.stock_logs:
    l_date = datetime.datetime.strptime(l["date"], "%Y-%m-%d").date()
    if not (start_d <= l_date <= end_d):
        continue
    if filter_c != "전체" and l["client"] != filter_c:
        continue
    if filter_wh != "전체" and l["wh"] != filter_wh:
        continue
    if search_kw:
        kw = search_kw.lower()
        if (kw not in l["prod_name"].lower() and 
            kw not in l.get("jan", "").lower() and 
            kw not in l.get("po_no", "").lower()):
            continue
    filtered_logs.append(l)

st.markdown("---")
st.write(f"**총 {len(filtered_logs)} 건의 입출고 내역이 검색되었습니다.**")

if filtered_logs:
    df_hist = pd.DataFrame(filtered_logs)[[
        "po_no", "date", "type", "wh", "client", "prod_name", "jan", "qty",
        "unit_price", "total_price", "trade_type", "zipcode", "ship_to", "manager"
    ]]
    df_hist.columns = [
        "발주/입출고번호", "날짜", "구분", "창고", "거래처", "상품명", "JAN/바코드",
        "수량", "단가(엔)", "총금액(엔)", "거래방식", "우편번호", "배송지정보", "담당자"
    ]
    st.dataframe(df_hist, use_container_width=True)
else:
    st.info("조건에 일치하는 이력이 없습니다.")
