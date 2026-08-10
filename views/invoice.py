import streamlit as st
from utils.supabase_client import supabase

def render():
    st.header("📄 청구 및 정산 관리")
    tab1, tab2 = st.tabs(["월별 합산 청구서 생성", "청구서 및 정산 내역"])
    
    with tab1:
        st.subheader("월별 납품 합산 Invoice 자동 생성")
        
        # 1. 거래처 목록 불러오기
        customers_res = supabase.table("customers").select("id, name").eq("is_active", True).execute()
        customer_options = {c["name"]: c["id"] for c in customers_res.data} if customers_res.data else {}

        if not customer_options:
            st.warning("등록된 거래처가 없습니다. 먼저 마스터 데이터에서 거래처를 등록해 주세요.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_customer = st.selectbox("거래처 선택", list(customer_options.keys()))
            with col2:
                year_month = st.text_input("대상 연월 (YYYY-MM)", value="2026-08")
            with col3:
                invoice_type = st.selectbox("청구 유형", ["NORMAL", "FOC", "SAMPLE"])
                
            if st.button("⚡ 월합산 Invoice 자동 생성"):
                try:
                    customer_id = customer_options[selected_customer]
                    # Supabase DB 저장 프로시저(fn_generate_monthly_invoice) 호출
                    response = supabase.rpc(
                        "fn_generate_monthly_invoice",
                        {
                            "p_customer_id": customer_id,
                            "p_year_month": year_month,
                            "p_invoice_type": invoice_type
                        }
                    ).execute()
                    
                    st.success(f"[{selected_customer}] {year_month} 월합산 청구서(Invoice)가 정상적으로 생성되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"청구서 생성 실패 (해당 기간 배송건 확인 필요): {e}")

    with tab2:
        st.subheader("발행된 청구서(Invoice) 목록")
        try:
            invoices = supabase.table("invoices").select("*").execute()
            if invoices.data:
                st.dataframe(invoices.data, use_container_width=True)
            else:
                st.info("발행된 청구서 내역이 없습니다.")
        except Exception as e:
            st.error(f"청구서 목록 조회 실패: {e}")
