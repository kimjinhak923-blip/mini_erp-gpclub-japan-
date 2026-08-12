import streamlit as st
import pandas as pd
from utils.db_client import supabase
from utils.auth import require_auth

# Streamlit 설정은 최상단에 배치
st.set_page_config(page_title="ERP System", page_icon="🏢", layout="wide")

# 로그인 인증 수행 (미인증 시 여기서 화면이 멈추고 로그인 화면 표시)
require_auth()

# --- 이 아래부터 기존 페이지 기능 코드 작성 ---

st.set_page_config(page_title="EC Sales System", page_icon="🛒", layout="wide")
st.title("🛒 EC Sales & Settlement (이커머스 매출 및 정산 관리)")
st.caption("해외/국내 이커머스 채널별 매출 수집, 통화 환율 적용 및 정산 집계")

tab1, tab2, tab3 = tab1, tab2, tab3 = st.tabs(["➕ EC 매출 수동/일괄 등록", "💱 통화 환율 및 정산 현황", "📊 채널별 매출 집계"])

# ==========================================
# 1. EC 매출 수동 및 CSV 일괄 등록
# ==========================================
with tab1:
    st.subheader("📥 EC 매출 데이터 등록")
    
    sub_tab1, sub_tab2 = st.tabs(["건별 직접 입력", "📂 CSV 파일 일괄 업로드"])
    
    with sub_tab1:
        with st.form("ec_single_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            platform = col1.selectbox("판매 플랫폼*", ["Amazon JP", "Rakuten", "Qoo10 JP", "Shopify", "Coupang", "기타"])
            ec_order_no = col2.text_input("EC 주문번호*", placeholder="250-1234567-8901234")
            sale_date = col3.date_input("판매 일자", datetime.now())
            
            col4, col5, col6 = st.columns(3)
            product_name = col4.text_input("판매 상품명*", placeholder="스마트센서 모듈 패키지")
            amount = col5.number_input("매출 금액 (원화/외화)*", min_value=0.0, value=10000.0, step=1000.0)
            currency = col6.selectbox("결제 통화*", ["JPY", "USD", "KRW", "EUR"])
            
            submitted_ec = st.form_submit_button("🚀 EC 매출 등록")
            
            if submitted_ec:
                if not ec_order_no or not product_name:
                    st.error("EC 주문번호와 상품명은 필수 입력 항목입니다.")
                else:
                    try:
                        supabase.table("ec_sales").insert({
                            "platform": platform,
                            "ec_order_no": ec_order_no,
                            "sale_date": str(sale_date),
                            "product_name": product_name,
                            "amount": amount,
                            "currency": currency,
                            "status": "SETTLED"
                        }).execute()
                        st.success(f"EC 매출건({ec_order_no})이 성공적으로 등록되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"등록 실패: {e}")

    with sub_tab2:
        st.markdown("##### 📂 CSV 일괄 등록")
        st.caption("CSV 필수 컬럼: `platform`, `ec_order_no`, `sale_date`, `product_name`, `amount`, `currency`")
        
        uploaded_file = st.file_uploader("EC 매출 CSV 파일 업로드", type=["csv"])
        if uploaded_file is not None:
            try:
                df_upload = pd.read_csv(uploaded_file)
                st.dataframe(df_upload.head(), use_container_width=True)
                
                if st.button("💾 데이터베이스에 일괄 저장"):
                    records = df_upload.to_dict(orient="records")
                    supabase.table("ec_sales").insert(records).execute()
                    st.success(f"총 {len(records)}건의 EC 매출 데이터가 저장되었습니다.")
                    st.rerun()
            except Exception as e:
                st.error(f"CSV 파일 처리 중 오류 발생: {e}")


# ==========================================
# 2. 통화 환율 및 정산 현황
# ==========================================
with tab2:
    st.subheader("💱 통화 환율 적용 원화(KRW) 환산 정산")
    
    col_ex1, col_ex2 = st.columns(2)
    jpy_rate = col_ex1.number_input("엔화 환율 (100 JPY 당 KRW)", value=900.0, step=10.0)
    usd_rate = col_ex2.number_input("달러 환율 (1 USD 당 KRW)", value=1350.0, step=10.0)
    
    res_ec = supabase.table("ec_sales").select("*").order("sale_date", desc=True).execute()
    
    if res_ec.data:
        df_ec = pd.DataFrame(res_ec.data)
        
        # 환율 적용 원화 계산 함수
        def calc_krw(row):
            amt = float(row["amount"] or 0)
            curr = row["currency"]
            if curr == "JPY":
                return amt * (jpy_rate / 100.0)
            elif curr == "USD":
                return amt * usd_rate
            else:
                return amt

        df_ec["원화 환산 금액(KRW)"] = df_ec.apply(calc_krw, axis=1)
        
        # Summary
        total_krw = df_ec["원화 환산 금액(KRW)"].sum()
        jpy_total = df_ec[df_ec["currency"] == "JPY"]["amount"].sum()
        usd_total = df_ec[df_ec["currency"] == "USD"]["amount"].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("총 환산 매출액 (KRW)", f"₩{total_krw:,.0f}")
        m2.metric("총 JPY 매출액", f"¥{jpy_total:,.0f}")
        m3.metric("총 USD 매출액", f"${usd_total:,.2f}")
        
        st.divider()
        
        display_df = df_ec[["platform", "ec_order_no", "sale_date", "product_name", "amount", "currency", "원화 환산 금액(KRW)"]]
        display_df.columns = ["플랫폼", "주문번호", "판매일자", "상품명", "결제금액", "통화", "KRW 환산 금액"]
        
        st.dataframe(
            display_df.style.format({
                "결제금액": "{:,.2f}",
                "KRW 환산 금액": "₩{:,.0f}"
            }),
            use_container_width=True
        )
    else:
        st.info("등록된 EC 매출 데이터가 없습니다.")


# ==========================================
# 3. 채널별 매출 집계
# ==========================================
with tab3:
    st.subheader("📊 플랫폼/채널별 매출 분석")
    
    res_chart = supabase.table("ec_sales").select("*").execute()
    if res_chart.data:
        df_chart = pd.DataFrame(res_chart.data)
        df_chart["KRW_Amount"] = df_chart.apply(
            lambda r: float(r["amount"]) * (jpy_rate / 100.0) if r["currency"] == "JPY" 
            else (float(r["amount"]) * usd_rate if r["currency"] == "USD" else float(r["amount"])), axis=1
        )
        
        platform_summary = df_chart.groupby("platform")["KRW_Amount"].sum().reset_index()
        platform_summary.columns = ["플랫폼", "총 매출액 (KRW)"]
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("##### 📌 플랫폼별 매출 요약")
            st.dataframe(platform_summary.style.format({"총 매출액 (KRW)": "₩{:,.0f}"}), use_container_width=True)
            
        with col_c2:
            st.markdown("##### 📈 플랫폼별 매출 비중")
            st.bar_chart(data=platform_summary, x="플랫폼", y="총 매출액 (KRW)")
    else:
        st.info("집계할 EC 매출 데이터가 없습니다.")
