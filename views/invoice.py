import streamlit as st

def render():
    st.header("📄 청구 및 정산 관리")
    tab1, tab2 = st.tabs(["월별 청구서 자동 생성", "정산 관리"])
    
    with tab1:
        st.subheader("월 합산 Invoice 생성")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("거래처 선택", ["Customer A", "Customer B"])
        with col2:
            st.text_input("대상 연월", value="2026-08")
            
        if st.button("월합산 Invoice 생성"):
            # Supabase fn_generate_monthly_invoice() 함수 호출
            st.success("해당 월의 미청구 배송건이 1장의 Invoice로 생성되었습니다.")
