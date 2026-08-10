import streamlit as st
from utils.supabase_client import supabase

def render():
    st.header("📦 마스터 데이터 관리")
    tab1, tab2, tab3 = st.tabs(["거래처 관리", "상품 관리", "창고 관리"])
    
    with tab1:
        st.subheader("거래처 목록")
        
        # 1. 거래처 등록 폼
        with st.expander("➕ 새 거래처 등록"):
            with st.form("add_customer_form"):
                code = st.text_input("거래처 코드 (예: CUST-001)")
                name = st.text_input("거래처명")
                email = st.text_input("이메일")
                phone = st.text_input("연락처")
                submitted = st.form_submit_button("저장")
                
                if submitted and code and name:
                    try:
                        supabase.table("customers").insert({
                            "code": code,
                            "name": name,
                            "email": email,
                            "phone": phone
                        }).execute()
                        st.success(f"거래처 '{name}' 등록 완료!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"등록 실패: {e}")

        # 2. 거래처 목록 조회
        try:
            response = supabase.table("customers").select("*").eq("is_active", True).execute()
            customers = response.data
            if customers:
                st.dataframe(customers, use_container_width=True)
            else:
                st.info("등록된 거래처가 없습니다.")
        except Exception as e:
            st.error(f"데이터를 불러오는데 실패했습니다: {e}")

    with tab2:
        st.subheader("상품(SKU) 목록")
        try:
            response = supabase.table("products").select("*").eq("is_active", True).execute()
            st.dataframe(response.data, use_container_width=True)
        except Exception as e:
            st.error(f"상품 목록 조회 실패: {e}")

    with tab3:
        st.subheader("창고 목록")
        try:
            response = supabase.table("warehouses").select("*").eq("is_active", True).execute()
            st.dataframe(response.data, use_container_width=True)
        except Exception as e:
            st.error(f"창고 목록 조회 실패: {e}")
