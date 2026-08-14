import streamlit as st

st.set_page_config(page_title="거래처 관리", layout="wide")

import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

st.title("🤝 거래처 관리")
st.markdown("---")

lang = st.session_state.get("lang", "한국어")

CLIENT_MAPS = {
    "한국어": {
        "client_name": "거래처명",
        "business_type": "업태/구분",
        "contact_person": "담당자명",
        "phone": "전화번호",
        "email": "이메일",
        "postal_code": "우편번호",
        "address": "주소"
    },
    "日本語": {
        "client_name": "取引先名",
        "business_type": "業態/区分",
        "contact_person": "担当者名",
        "phone": "電話番号",
        "email": "メールアドレス",
        "postal_code": "郵便番号",
        "address": "住所"
    },
    "English": {
        "client_name": "Client Name",
        "business_type": "Business Type",
        "contact_person": "Contact Person",
        "phone": "Phone",
        "email": "Email",
        "postal_code": "Postal Code",
        "address": "Address"
    }
}

tab1, tab2 = st.tabs(["🏢 거래처 목록 관리", "➕ 거래처 신규 등록"])

with tab1:
    st.subheader("등록된 거래처 현황")
    if st.session_state.clients:
        df_c = pd.DataFrame(st.session_state.clients)
        df_c_renamed = df_c.rename(columns=CLIENT_MAPS.get(lang, CLIENT_MAPS["한국어"]))
        edited_c = st.data_editor(df_c_renamed, num_rows="dynamic", use_container_width=True)
        if st.button("💾 거래처 정보 저장"):
            inv_map = {v: k for k, v in CLIENT_MAPS.get(lang, CLIENT_MAPS["한국어"]).items()}
            st.session_state.clients = edited_c.rename(columns=inv_map).to_dict("records")
            st.success("거래처 정보가 저장되었습니다.")
            st.rerun()

with tab2:
    with st.form("add_client_form"):
        c1, c2 = st.columns(2)
        with c1:
            c_name = st.text_input("거래처명")
            b_type = st.selectbox("구분", ["도매", "소매", "온라인", "해외", "기타"])
            c_person = st.text_input("담당자명")
            phone = st.text_input("전화번호")
        with c2:
            email = st.text_input("이메일")
            p_code = st.text_input("우편번호")
            address = st.text_input("주소")

        if st.form_submit_button("거래처 등록"):
            if c_name:
                st.session_state.clients.append({
                    "client_name": c_name,
                    "business_type": b_type,
                    "contact_person": c_person,
                    "phone": phone,
                    "email": email,
                    "postal_code": p_code,
                    "address": address,
                })
                st.success("신규 거래처가 등록되었습니다.")
                st.rerun()
