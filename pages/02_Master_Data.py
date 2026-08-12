import streamlit as st
import pandas as pd
from utils.db_client import supabase

st.set_page_config(page_title="Master Data Management", page_icon="📂", layout="wide")
st.title("📂 Master Data Management")
st.caption("기초 기준 정보 (Customer, Supplier, Product, Warehouse) 관리 화면")

tab1, tab2, tab3, tab4 = st.tabs(["Customer (거래처)", "Supplier (공급처)", "Product (상품)", "Warehouse (창고)"])

# ==========================================
# 1. Customer Management (거래처 관리)
# ==========================================
with tab1:
    st.subheader("🏢 Customer (거래처) 관리")
    
    # --- 등록 폼 ---
    with st.expander("➕ 신규 거래처 등록", expanded=False):
        with st.form("customer_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            c_code = col1.text_input("거래처 코드 (필수)*", placeholder="CUST-001")
            c_name = col2.text_input("거래처명 (필수)*", placeholder="(주)ABC무역")
            c_contact = col1.text_input("담당자명")
            c_email = col2.text_input("이메일")
            c_phone = col1.text_input("전화번호")
            c_country = col2.text_input("국가", value="KR")
            c_currency = col1.selectbox("통화 단위", ["KRW", "JPY", "USD", "EUR"])
            
            submitted_c = st.form_submit_button("거래처 등록")
            if submitted_c:
                if not c_code or not c_name:
                    st.error("거래처 코드와 거래처명은 필수 입력 항목입니다.")
                else:
                    try:
                        supabase.table("customers").insert({
                            "customer_code": c_code,
                            "name": c_name,
                            "contact_person": c_contact,
                            "email": c_email,
                            "phone": c_phone,
                            "country": c_country,
                            "currency": c_currency,
                            "is_active": True
                        }).execute()
                        st.success(f"거래처 '{c_name}' 등록 성공!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"등록 실패: {e}")

    # --- 조회 및 수정/Soft Delete ---
    st.markdown("#### 📋 거래처 목록")
    show_inactive_c = st.checkbox("비활성화된(Soft Deleted) 거래처도 포함해서 보기", key="show_inc_c")
    
    query_c = supabase.table("customers").select("*")
    if not show_inactive_c:
        query_c = query_c.eq("is_active", True)
    
    res_c = query_c.order("created_at", desc=True).execute()
    
    if res_c.data:
        df_c = pd.DataFrame(res_c.data)
        
        # Data Editor를 통한 수정 및 Soft Delete 처리
        edited_df_c = st.data_editor(
            df_c,
            key="customer_editor",
            use_container_width=True,
            disabled=["id", "created_at"],
            column_config={
                "is_active": st.column_config.CheckboxColumn("사용 여부 (Uncheck시 Soft Delete)")
            }
        )
        
        if st.button("💾 Customer 변경사항 저장", key="save_c"):
            try:
                for idx, row in edited_df_c.iterrows():
                    supabase.table("customers").update({
                        "customer_code": row["customer_code"],
                        "name": row["name"],
                        "contact_person": row["contact_person"],
                        "email": row["email"],
                        "phone": row["phone"],
                        "country": row["country"],
                        "currency": row["currency"],
                        "is_active": row["is_active"]
                    }).eq("id", row["id"]).execute()
                st.success("Customer 변경사항이 정상 반영되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"저장 중 오류 발생: {e}")
    else:
        st.info("등록된 거래처 데이터가 없습니다.")


# ==========================================
# 2. Supplier Management (공급처 관리)
# ==========================================
with tab2:
    st.subheader("🏬 Supplier (공급처) 관리")
    
    with st.expander("➕ 신규 공급처 등록", expanded=False):
        with st.form("supplier_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            s_code = col1.text_input("공급처 코드 (필수)*", placeholder="SUP-001")
            s_name = col2.text_input("공급처명 (필수)*", placeholder="(주)글로벌원자재")
            s_contact = col1.text_input("담당자명")
            s_email = col2.text_input("이메일")
            s_phone = col1.text_input("전화번호")
            s_currency = col2.selectbox("기본 결제 통화", ["KRW", "JPY", "USD", "EUR"])
            
            submitted_s = st.form_submit_button("공급처 등록")
            if submitted_s:
                if not s_code or not s_name:
                    st.error("공급처 코드와 공급처명은 필수 입력 항목입니다.")
                else:
                    try:
                        supabase.table("suppliers").insert({
                            "supplier_code": s_code,
                            "name": s_name,
                            "contact_person": s_contact,
                            "email": s_email,
                            "phone": s_phone,
                            "currency": s_currency,
                            "is_active": True
                        }).execute()
                        st.success(f"공급처 '{s_name}' 등록 성공!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"등록 실패: {e}")

    st.markdown("#### 📋 공급처 목록")
    show_inactive_s = st.checkbox("비활성화된(Soft Deleted) 공급처도 포함해서 보기", key="show_inc_s")
    
    query_s = supabase.table("suppliers").select("*")
    if not show_inactive_s:
        query_s = query_s.eq("is_active", True)
        
    res_s = query_s.order("created_at", desc=True).execute()
    
    if res_s.data:
        df_s = pd.DataFrame(res_s.data)
        edited_df_s = st.data_editor(
            df_s,
            key="supplier_editor",
            use_container_width=True,
            disabled=["id", "created_at"],
            column_config={
                "is_active": st.column_config.CheckboxColumn("사용 여부 (Uncheck시 Soft Delete)")
            }
        )
        if st.button("💾 Supplier 변경사항 저장", key="save_s"):
            try:
                for idx, row in edited_df_s.iterrows():
                    supabase.table("suppliers").update({
                        "supplier_code": row["supplier_code"],
                        "name": row["name"],
                        "contact_person": row["contact_person"],
                        "email": row["email"],
                        "phone": row["phone"],
                        "currency": row["currency"],
                        "is_active": row["is_active"]
                    }).eq("id", row["id"]).execute()
                st.success("Supplier 변경사항이 정상 반영되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"저장 중 오류 발생: {e}")
    else:
        st.info("등록된 공급처 데이터가 없습니다.")


# ==========================================
# 3. Product Management (상품 Master 관리)
# ==========================================
with tab3:
    st.subheader("📦 Product (상품 Master) 관리")
    
    with st.expander("➕ 신규 상품 마스터 등록", expanded=False):
        with st.form("product_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_sku = col1.text_input("SKU 코드 (필수)*", placeholder="PROD-1001")
            p_name = col2.text_input("상품명 (필수)*", placeholder="스마트센서 모듈")
            p_brand = col1.text_input("브랜드명")
            p_category = col2.text_input("카테고리")
            p_s_price = col1.number_input("기본 판매가 (KRW)", min_value=0.0, step=1000.0)
            p_p_price = col2.number_input("기본 매입가 (KRW)", min_value=0.0, step=1000.0)
            
            submitted_p = st.form_submit_button("상품 등록")
            if submitted_p:
                if not p_sku or not p_name:
                    st.error("SKU와 상품명은 필수 입력 항목입니다.")
                else:
                    try:
                        supabase.table("products").insert({
                            "sku": p_sku,
                            "name": p_name,
                            "brand": p_brand,
                            "category": p_category,
                            "selling_price": p_s_price,
                            "purchase_price": p_p_price,
                            "is_active": True
                        }).execute()
                        st.success(f"상품 '{p_name}' 등록 성공!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"등록 실패: {e}")

    st.markdown("#### 📋 상품 목록")
    show_inactive_p = st.checkbox("비활성화된(Soft Deleted) 상품도 포함해서 보기", key="show_inc_p")
    
    query_p = supabase.table("products").select("*")
    if not show_inactive_p:
        query_p = query_p.eq("is_active", True)
        
    res_p = query_p.order("created_at", desc=True).execute()
    
    if res_p.data:
        df_p = pd.DataFrame(res_p.data)
        edited_df_p = st.data_editor(
            df_p,
            key="product_editor",
            use_container_width=True,
            disabled=["id", "created_at"],
            column_config={
                "selling_price": st.column_config.NumberColumn("판매가", format="₩%d"),
                "purchase_price": st.column_config.NumberColumn("매입가", format="₩%d"),
                "is_active": st.column_config.CheckboxColumn("사용 여부 (Uncheck시 Soft Delete)")
            }
        )
        if st.button("💾 Product 변경사항 저장", key="save_p"):
            try:
                for idx, row in edited_df_p.iterrows():
                    supabase.table("products").update({
                        "sku": row["sku"],
                        "name": row["name"],
                        "brand": row["brand"],
                        "category": row["category"],
                        "selling_price": row["selling_price"],
                        "purchase_price": row["purchase_price"],
                        "is_active": row["is_active"]
                    }).eq("id", row["id"]).execute()
                st.success("Product 변경사항이 정상 반영되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"저장 중 오류 발생: {e}")
    else:
        st.info("등록된 상품 데이터가 없습니다.")


# ==========================================
# 4. Warehouse Management (창고 관리)
# ==========================================
with tab4:
    st.subheader("🏭 Warehouse (창고 Master) 관리")
    
    with st.expander("➕ 신규 창고 등록", expanded=False):
        with st.form("warehouse_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            w_name = col1.text_input("창고명 (필수)*", placeholder="인천 제1물류센터")
            w_location = col2.text_input("위치/주소", placeholder="인천광역시 중구 ...")
            w_manager = col1.text_input("창고 담당자명")
            
            submitted_w = st.form_submit_button("창고 등록")
            if submitted_w:
                if not w_name:
                    st.error("창고명은 필수 입력 항목입니다.")
                else:
                    try:
                        supabase.table("warehouses").insert({
                            "name": w_name,
                            "location": w_location,
                            "manager_name": w_manager,
                            "is_active": True
                        }).execute()
                        st.success(f"창고 '{w_name}' 등록 성공!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"등록 실패: {e}")

    st.markdown("#### 📋 창고 목록")
    show_inactive_w = st.checkbox("비활성화된(Soft Deleted) 창고도 포함해서 보기", key="show_inc_w")
    
    query_w = supabase.table("warehouses").select("*")
    if not show_inactive_w:
        query_w = query_w.eq("is_active", True)
        
    res_w = query_w.order("created_at", desc=True).execute()
    
    if res_w.data:
        df_w = pd.DataFrame(res_w.data)
        edited_df_w = st.data_editor(
            df_w,
            key="warehouse_editor",
            use_container_width=True,
            disabled=["id", "created_at"],
            column_config={
                "is_active": st.column_config.CheckboxColumn("사용 여부 (Uncheck시 Soft Delete)")
            }
        )
        if st.button("💾 Warehouse 변경사항 저장", key="save_w"):
            try:
                for idx, row in edited_df_w.iterrows():
                    supabase.table("warehouses").update({
                        "name": row["name"],
                        "location": row["location"],
                        "manager_name": row["manager_name"],
                        "is_active": row["is_active"]
                    }).eq("id", row["id"]).execute()
                st.success("Warehouse 변경사항이 정상 반영되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"저장 중 오류 발생: {e}")
    else:
        st.info("등록된 창고 데이터가 없습니다.")
