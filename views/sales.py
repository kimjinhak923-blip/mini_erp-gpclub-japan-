import streamlit as st

def render():
    st.header("🛒 영업 및 배송 관리")
    tab1, tab2 = st.tabs(["수주 관리 (Customer Order)", "배송 관리 (Delivery)"])
    
    with tab1:
        st.subheader("수주 등록")
        st.text_input("Customer PO No. (필수 수동 입력)")
        st.info("동일 거래처 내 PO 번호 중복 방지 규칙이 적용됩니다.")
        
    with tab2:
        st.subheader("배송 처리 및 분할 납품")
        st.info("배송 완료 시 재고가 자동 차감됩니다.")
