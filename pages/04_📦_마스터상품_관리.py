import pandas as pd
import streamlit as st

user = st.session_state.get("logged_in_user")
if not user:
    st.warning("로그인이 필요한 페이지입니다. 메인 페이지에서 먼저 로그인해 주세요.")
    st.stop()

st.title("📦 마스터 상품 관리")
st.markdown("---")

tab1, tab2 = st.tabs(["📋 상품 목록 및 편집", "➕ 신규 상품 등록"])

with tab1:
    st.subheader("상품 데이터 목록")
    if st.session_state.master_products:
        df = pd.DataFrame(st.session_state.master_products)
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="master_editor",
        )
        if st.button("💾 변경사항 저장"):
            st.session_state.master_products = edited_df.to_dict("records")
            st.success("마스터 상품 정보가 변경되었습니다.")
            st.rerun()
    else:
        st.info("등록된 상품이 없습니다.")

with tab2:
    st.subheader("신규 상품 입력")
    with st.form("add_product_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            jan_code = st.text_input("JAN 코드 (바코드)")
            product_name = st.text_input("상품명")
            category = st.text_input("카테고리", value="스킨케어")
            capacity = st.text_input("용량/규격", value="50ml")
        with col2:
            units_per_box = st.number_input("박스당 입수량(EA)", min_value=1, value=24)
            box_cbm = st.number_input("박스 CBM", min_value=0.0, value=0.02, format="%.3f")
            box_weight_kg = st.number_input("박스 중량(kg)", min_value=0.0, value=10.0)
            plt_qty = st.number_input("PLT당 박스 수", min_value=1, value=40)
        with col3:
            supply_price_jpy = st.number_input("공급 단가(엔)", min_value=0, value=1000)
            list_price_jpy = st.number_input("소비자 가(엔)", min_value=0, value=2000)
            memo = st.text_input("비고/메모")

        submit = st.form_submit_button("상품 등록")
        if submit:
            if not jan_code or not product_name:
                st.error("JAN 코드와 상품명은 필수 입력 항목입니다.")
            else:
                exists = any(
                    p["jan_code"] == jan_code for p in st.session_state.master_products
                )
                if exists:
                    st.error("이미 존재하는 JAN 코드입니다.")
                else:
                    new_p = {
                        "jan_code": jan_code,
                        "product_name": product_name,
                        "category": category,
                        "capacity": capacity,
                        "units_per_box": units_per_box,
                        "box_cbm": box_cbm,
                        "box_weight_kg": box_weight_kg,
                        "plt_qty": plt_qty,
                        "supply_price_jpy": supply_price_jpy,
                        "list_price_jpy": list_price_jpy,
                        "memo": memo,
                    }
                    st.session_state.master_products.append(new_p)
                    st.success(f"상품 [{product_name}] 등록 완료!")
                    st.rerun()
