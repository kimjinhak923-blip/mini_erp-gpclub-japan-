import pandas as pd
import streamlit as st

user = st.session_state.get("logged_in_user")
if not user:
    st.warning("로그인이 필요한 페이지입니다. 메인 페이지에서 먼저 로그인해 주세요.")
    st.stop()

st.title("📜 입출고 통합 이력 조회")
st.markdown("---")

if not st.session_state.stock_logs:
    st.info("입출고 이력이 존재하지 않습니다.")
else:
    df_logs = pd.DataFrame(st.session_state.stock_logs)

    c1, c2, c3 = st.columns(3)
    with c1:
        type_filter = st.multiselect(
            "구분 필터", ["입고", "출고"], default=["입고", "출고"]
        )
    with c2:
        wh_filter = st.multiselect(
            "창고 필터",
            st.session_state.warehouses,
            default=st.session_state.warehouses,
        )
    with c3:
        search_kw = st.text_input("검색어 (상품명, JAN, 거래처)", "")

    filtered_df = df_logs[
        (df_logs["type"].isin(type_filter)) & (df_logs["warehouse"].isin(wh_filter))
    ]

    if search_kw:
        filtered_df = filtered_df[
            filtered_df["product_name"].str.contains(search_kw, na=False)
            | filtered_df["jan_code"].str.contains(search_kw, na=False)
            | filtered_df["client_name"].str.contains(search_kw, na=False)
        ]

    st.dataframe(filtered_df, use_container_width=True)
