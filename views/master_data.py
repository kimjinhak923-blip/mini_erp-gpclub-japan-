import streamlit as st

def render():
    st.header("📦 마스터 데이터 관리")
    tab1, tab2, tab3 = st.tabs(["거래처 관리", "상품 관리", "창고 관리"])
    
    with tab1:
        st.subheader("거래처 목록")
        # DB 조회 및 등록 UI 구현 위치
        st.info("등록된 거래처 및 공급처 정보를 관리합니다.")
        
    with tab2:
        st.subheader("상품(SKU) 목록")
        st.info("SKU별 판매가, 구매가, 바코드 정보를 관리합니다.")

    with tab3:
        st.subheader("창고 목록")
        st.info("거점별 창고 정보를 관리합니다.")
