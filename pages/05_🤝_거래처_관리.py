import pandas as pd
import streamlit as st

st.set_page_config(page_title="거래처 관리", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

user = st.session_state.logged_in_user
is_admin = user.get("role") == "관리자" or user["id"] == "admin"
is_visitor = user.get("role") == "방문자"

st.header("🤝 거래처 및 거래제품 관리")

tab1, tab2, tab3 = st.tabs(["🏢 등록 거래처 & 상세 제품 조회", "➕ 신규 거래처 등록", "📦 거래처 제품 등록"])

with tab1:
    st.subheader("🏢 현재 등록된 거래처 목록")
    if st.session_state.clients:
        st.dataframe(pd.DataFrame(st.session_state.clients), use_container_width=True)

        st.markdown("---")
        c_names = [c["name"] for c in st.session_state.clients]
        sel_c = st.selectbox("거래처 선택", c_names)
        target_c = next(c for c in st.session_state.clients if c["name"] == sel_c)

        with st.expander(f"🛠️ [{sel_c}] 거래처 정보 수정 / 삭제"):
            e_zip = st.text_input("우편번호", value=target_c.get("zipcode", ""))
            e_addr = st.text_input("주소", value=target_c.get("address", ""))
            e_phone = st.text_input("전화번호", value=target_c.get("phone", ""))

            b_c1, b_c2 = st.columns(2)
            if b_c1.button("거래처 저장", disabled=is_visitor):
                target_c["zipcode"] = e_zip
                target_c["address"] = e_addr
                target_c["phone"] = e_phone
                st.success("수정 완료")
                st.rerun()
            if b_c2.button("❌ 거래처 삭제", disabled=not is_admin):
                st.session_state.clients.remove(target_c)
                st.session_state.client_products = [cp for cp in st.session_state.client_products if cp["client_name"] != sel_c]
                st.success("삭제 완료")
                st.rerun()

        st.subheader(f"📦 [{sel_c}] 등록된 거래 제품 목록")
        m_cps = [cp for cp in st.session_state.client_products if cp["client_name"] == sel_c]

        if m_cps:
            st.dataframe(pd.DataFrame(m_cps), use_container_width=True)

            with st.expander("🛠️ 거래 제품 수정 / 삭제"):
                cp_names = [cp["prod_name"] for cp in m_cps]
                sel_cp = st.selectbox("제품 선택", cp_names)
                target_cp = next(cp for cp in m_cps if cp["prod_name"] == sel_cp)

                e_cp_price = st.number_input("공급가(엔 vat-)", min_value=0, value=int(target_cp["supply_price"]))
                e_cp_jan = st.text_input("JAN(곽)", value=target_cp.get("jan_pack", ""))

                cp1, cp2 = st.columns(2)
                if cp1.button("제품 저장", disabled=is_visitor):
                    target_cp["supply_price"] = e_cp_price
                    target_cp["jan_pack"] = e_cp_jan
                    st.success("제품 정보 수정 완료")
                    st.rerun()
                if cp2.button("❌ 제품 삭제", disabled=not is_admin):
                    st.session_state.client_products.remove(target_cp)
                    st.success("제품 삭제 완료")
                    st.rerun()

with tab2:
    st.subheader("➕ 신규 거래처 등록")
    with st.form("new_client_form"):
        nc_name = st.text_input("거래처명 *")
        nc_zip = st.text_input("우편번호 (예: 100-0001)")
        nc_addr = st.text_input("주소 *")
        nc_phone = st.text_input("전화번호 *")

        if st.form_submit_button("거래처 등록", disabled=is_visitor):
            if not nc_name or not nc_addr:
                st.error("필수 항목을 입력해 주세요.")
            else:
                st.session_state.clients.append({
                    "id": len(st.session_state.clients) + 1,
                    "name": nc_name,
                    "zipcode": nc_zip,
                    "address": nc_addr,
                    "phone": nc_phone,
                })
                st.success("등록 완료!")
                st.rerun()

with tab3:
    st.subheader("📦 거래처 제품 등록")
    if st.session_state.clients:
        c_names = [c["name"] for c in st.session_state.clients]
        target_c_p = st.selectbox("대상 거래처 선택", c_names)

        with st.form("new_client_prod_form"):
            ncp_name = st.text_input("상품명 *")
            ncp_jan_p = st.text_input("JAN(곽)")
            ncp_jan_s = st.text_input("JAN(낱장)")
            ncp_price = st.number_input("공급가(엔 VAT 별도) *", min_value=0, step=100)

            if st.form_submit_button("거래제품 등록", disabled=is_visitor):
                if not ncp_name:
                    st.error("상품명은 필수입니다.")
                else:
                    st.session_state.client_products.append({
                        "client_name": target_c_p,
                        "prod_name": ncp_name,
                        "jan_pack": ncp_jan_p,
                        "jan_single": ncp_jan_s,
                        "supply_price": ncp_price,
                    })
                    st.success("등록 완료!")
                    st.rerun()
