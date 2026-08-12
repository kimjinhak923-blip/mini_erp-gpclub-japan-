import pandas as pd
import streamlit as st

user = st.session_state.get("logged_in_user")

st.title("🏢 거래처 및 단가 관리")
st.markdown("---")

if not user:
    st.warning("로그인이 필요한 페이지입니다. 메인 페이지에서 먼저 로그인해 주세요.")
else:
    tab1, tab2, tab3 = st.tabs(["🏢 거래처 목록", "➕ 거래처 등록", "💰 거래처별 전용 단가"])

    with tab1:
        st.subheader("등록된 거래처 목록")
        if st.session_state.clients:
            df_clients = pd.DataFrame(st.session_state.clients)
            edited_clients = st.data_editor(
                df_clients, num_rows="dynamic", use_container_width=True
            )
            if st.button("💾 거래처 정보 저장"):
                st.session_state.clients = edited_clients.to_dict("records")
                st.success("거래처 정보가 저장되었습니다.")
                st.rerun()
        else:
            st.info("등록된 거래처가 없습니다.")

    with tab2:
        st.subheader("신규 거래처 등록")
        with st.form("client_form"):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("거래처명")
                b_type = st.selectbox("업태/유형", ["도매", "소매", "온라인", "기타"])
                person = st.text_input("담당자명")
                phone = st.text_input("전화번호")
            with c2:
                email = st.text_input("이메일")
                postal = st.text_input("우편번호")
                address = st.text_input("주소")

            sub = st.form_submit_button("거래처 등록")
            if sub:
                if not c_name:
                    st.error("거래처명은 필수입니다.")
                else:
                    st.session_state.clients.append({
                        "client_name": c_name,
                        "business_type": b_type,
                        "contact_person": person,
                        "phone": phone,
                        "email": email,
                        "postal_code": postal,
                        "address": address,
                    })
                    st.success("거래처가 성공적으로 등록되었습니다.")
                    st.rerun()

    with tab3:
        st.subheader("거래처별 전용 공급단가 지정")
        if st.session_state.clients and st.session_state.master_products:
            c_list = [c["client_name"] for c in st.session_state.clients]
            selected_client = st.selectbox("거래처 선택", c_list)
            p_list = [
                f"{p['product_name']} ({p['jan_code']})"
                for p in st.session_state.master_products
            ]
            selected_prod = st.selectbox("상품 선택", p_list)
            custom_price = st.number_input("전용 공급 단가(엔)", min_value=0, value=1000)

            if st.button("단가 설정 저장"):
                jan = selected_prod.split("(")[-1].replace(")", "")
                p_name = selected_prod.split(" (")[0]
                st.session_state.client_products.append({
                    "client_name": selected_client,
                    "jan_code": jan,
                    "product_name": p_name,
                    "custom_supply_price": custom_price,
                })
                st.success("전용 단가가 설정되었습니다.")

            st.markdown("---")
            st.write("📋 **현재 설정된 전용 단가 목록**")
            if st.session_state.client_products:
                st.dataframe(
                    pd.DataFrame(st.session_state.client_products),
                    use_container_width=True,
                )
        else:
            st.warning("거래처와 마스터 상품이 최소 1개 이상 존재해야 합니다.")
