import streamlit as st

def render():
    st.header("🏭 재고 및 창고 이동")
    tab1, tab2 = st.tabs(["창고별 현황", "창고 간 재고 이동"])
    
    with tab1:
        st.subheader("실시간 재고 현황")
        st.info("현재 재고, 예약 재고, 입출고 예정 수량을 확인합니다.")
        
    with tab2:
        st.subheader("재고 이동 요청")
        st.info("이동 완료 시 출발 창고 감소, 도착 창고 증가 트랜잭션이 자동 실행됩니다.")
