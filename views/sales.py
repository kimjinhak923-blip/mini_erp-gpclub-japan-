import streamlit as st
from utils.supabase_client import supabase

def render():
    st.header("🛒 영업 및 배송 관리")
    tab1, tab2 = st.tabs(["수주 관리 (Sales Order)", "배송 관리 (Delivery)"])
    
    with tab1:
        st.subheader("수주 등록 및 조회")
        
        # 1. 거래처 목록 불러오기
        customers_res = supabase.table("customers").select("id, name").eq("is_active", True).execute()
        customer_options = {c["name"]: c["id"] for c in customers_res.data} if customers_res.data else {}

        with st.expander("➕ 새 수주 등록"):
            if not customer_options:
                st.warning("먼저 마스터 데이터에서 거래처를 등록해 주세요.")
            else:
                with st.form("add_sales_order_form"):
                    selected_customer_name = st.selectbox("거래처 선택", list(customer_options.keys()))
                    customer_po_no = st.text_input("Customer PO 번호 (필수 수동 입력)")
                    order_date = st.date_input("수주일자")
                    total_amount = st.number_input("총 금액", min_value=0.0, step=1000.0)
                    note = st.text_area("비고")
                    submitted = st.form_submit_button("수주 저장")
                    
                    if submitted and customer_po_no:
                        try:
                            supabase.table("sales_orders").insert({
                                "customer_id": customer_options[selected_customer_name],
                                "customer_po_no": customer_po_no,
                                "order_date": str(order_date),
                                "total_amount": total_amount,
                                "note": note,
                                "status": "APPROVED"
                            }).execute()
                            st.success(f"PO [{customer_po_no}] 수주 등록 완료!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"수주 등록 실패 (동일 거래처 중복 PO 여부 확인): {e}")

        # 2. 수주 목록 조회
        try:
            orders = supabase.table("sales_orders").select("id, customer_po_no, order_date, status, total_amount, created_at").eq("is_active", True).execute()
            if orders.data:
                st.dataframe(orders.data, use_container_width=True)
            else:
                st.info("등록된 수주 건이 없습니다.")
        except Exception as e:
            st.error(f"수주 목록 조회 실패: {e}")

    with tab2:
        st.subheader("배송 현황 조회")
        try:
            deliveries = supabase.table("deliveries").select("*").execute()
            if deliveries.data:
                st.dataframe(deliveries.data, use_container_width=True)
            else:
                st.info("진행 중인 배송 내역이 없습니다.")
        except Exception as e:
            st.error(f"배송 목록 조회 실패: {e}")
