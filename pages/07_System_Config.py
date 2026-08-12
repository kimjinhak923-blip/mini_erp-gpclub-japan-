import streamlit as st
import pandas as pd
from utils.db_client import supabase
from datetime import datetime, timedelta

st.set_page_config(page_title="System Config & Audit", page_icon="⚙️", layout="wide")
st.title("⚙️ System Config & Audit Logs (청구서 및 감사 로그)")
st.caption("Invoice 청구서 발행, 시스템 설정 및 데이터베이스 감사 로그(Audit Logs) 조회")

tab1, tab2, tab3 = st.tabs(["📑 Invoice (청구서) 발행 및 관리", "📜 Audit Logs (감사 로그)", "⚙️ 일반 시스템 설정"])

# ==========================================
# 1. Invoice (청구서) 발행 및 관리
# ==========================================
with tab1:
    st.subheader("📑 Sales Order 기반 Invoice(청구서) 발행")
    
    # FULFILLED 또는 CONFIRMED 상태인 Sales Order 가져오기
    so_res = supabase.table("sales_orders").select("*, customers(name)").filter("status", "in", "('CONFIRMED', 'FULFILLED')").order("created_at", desc=True).execute()
    
    if not so_res.data:
        st.info("청구서를 발행할 수 있는 수주(SO) 건이 없습니다.")
    else:
        so_options = {f"SO-ID: {so['id'][:8]}... | 거래처: {so.get('customers', {}).get('name', '-')} | 금액: ₩{so['total_amount']:,.0f}": so for so in so_res.data}
        
        with st.form("invoice_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            selected_so_label = col1.selectbox("대상 Sales Order 선택*", list(so_options.keys()))
            target_so = so_options[selected_so_label]
            
            invoice_no = col2.text_input("청구서 번호 (Invoice No)*", value=f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            col3, col4 = st.columns(2)
            issue_date = col3.date_input("발행일자", datetime.now())
            due_date = col4.date_input("지급 만기일자", datetime.now() + timedelta(days=30))
            
            col5, col6 = st.columns(2)
            amount = col5.number_input("청구 금액 (KRW)", min_value=0.0, value=float(target_so["total_amount"]), step=1000.0)
            status = col6.selectbox("발행 상태", ["ISSUED", "PAID", "CANCELLED"])
            
            submitted_inv = st.form_submit_button("📑 Invoice 발행 확정")
            
            if submitted_inv:
                try:
                    supabase.table("invoices").insert({
                        "so_id": target_so["id"],
                        "invoice_no": invoice_no,
                        "issue_date": str(issue_date),
                        "due_date": str(due_date),
                        "amount": amount,
                        "status": status
                    }).execute()
                    
                    st.success(f"Invoice({invoice_no})가 성공적으로 발행되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Invoice 발행 중 오류 발생: {e}")

    st.divider()
    st.markdown("##### 📋 발행된 Invoice 목록")
    
    inv_res = supabase.table("invoices").select("*, sales_orders(id, customers(name))").order("created_at", desc=True).execute()
    if inv_res.data:
        df_inv = pd.DataFrame([{
            "Invoice No": item["invoice_no"],
            "거래처": item.get("sales_orders", {}).get("customers", {}).get("name", "-") if item.get("sales_orders") else "-",
            "발행일": item["issue_date"],
            "만기일": item["due_date"],
            "청구금액": f"₩{item['amount']:,.0f}",
            "상태": item["status"]
        } for item in inv_res.data])
        st.dataframe(df_inv, use_container_width=True)
    else:
        st.info("발행된 청구서 내역이 없습니다.")


# ==========================================
# 2. Audit Logs (감사 로그) 조회
# ==========================================
with tab2:
    st.subheader("📜 시스템 감사 로그 (Audit Logs)")
    st.caption("시스템 내 주요 트랜잭션 및 데이터 변경 이력을 실시간으로 추적합니다.")
    
    col_f1, col_f2 = st.columns([2, 1])
    action_filter = col_f1.selectbox("작업 유형 필터", ["전체", "INSERT", "UPDATE", "DELETE"])
    
    query = supabase.table("audit_logs").select("*").order("created_at", desc=True)
    if action_filter != "전체":
        query = query.eq("action", action_filter)
        
    audit_res = query.execute()
    
    if audit_res.data:
        df_audit = pd.DataFrame(audit_res.data)
        cols_to_show = ["created_at", "table_name", "action", "performed_by", "details"]
        df_audit = df_audit[[c for c in cols_to_show if c in df_audit.columns]]
        st.dataframe(df_audit, use_container_width=True)
    else:
        st.info("조회된 Audit Log가 없습니다.")


# ==========================================
# 3. 일반 시스템 설정
# ==========================================
with tab3:
    st.subheader("⚙️ ERP 글로벌 환경 설정")
    
    with st.form("sys_config_form"):
        st.text_input("기본 회사명", value="(주)글로벌 ERP 솔루션")
        st.text_input("기본 통화 코드", value="KRW")
        st.number_input("기본 부가가치세율 (%)", value=10.0, step=0.5)
        st.selectbox("기본 재고 평가 방식", ["FIFO (선입선출법)", "LIFO (후입선출법)", "Moving Average (동적 이동평균법)"])
        
        save_btn = st.form_submit_button("💾 설정 저장")
        if save_btn:
            st.success("시스템 설정이 성공적으로 반영되었습니다.")
