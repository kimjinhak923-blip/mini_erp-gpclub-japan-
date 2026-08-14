import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# 1. 다국어 딕셔너리 정의 (한국어 / 일본어 / 영어)
TRANSLATIONS = {
    "KO": {
        "page_title": "거래처 관리",
        "title": "🤝 거래처 관리",
        "tab1": "🏢 거래처 목록 관리",
        "tab2": "➕ 거래처 신규 등록",
        "sub_tab1": "등록된 거래처 현황",
        "btn_save_clients": "💾 거래처 정보 저장",
        "msg_save_success": "거래처 정보가 저장되었습니다.",
        "msg_no_clients": "등록된 거래처가 없습니다. 신규 거래처를 등록해주세요.",
        "form_c_name": "거래처명",
        "form_b_type": "업태/구분",
        "b_type_options": ["도매", "소매", "온라인", "해외", "기타"],
        "form_c_person": "담당자명",
        "form_phone": "전화번호",
        "form_email": "이메일",
        "form_postal": "우편번호",
        "form_address": "주소",
        "btn_add_client": "거래처 등록",
        "msg_add_success": "신규 거래처가 등록되었습니다.",
        "msg_name_required": "거래처명을 입력해주세요.",
    },
    "JA": {
        "page_title": "取引先管理",
        "title": "🤝 取引先管理",
        "tab1": "🏢 取引先一覧管理",
        "tab2": "➕ 取引先新規登録",
        "sub_tab1": "登録済み取引先一覧",
        "btn_save_clients": "💾 取引先情報を保存",
        "msg_save_success": "取引先情報が保存されました。",
        "msg_no_clients": "登録された取引先がありません。新規取引先を登録してください。",
        "form_c_name": "取引先名",
        "form_b_type": "業態/区分",
        "b_type_options": ["卸売", "小売", "オンライン", "海外", "その他"],
        "form_c_person": "担当者名",
        "form_phone": "電話番号",
        "form_email": "メールアドレス",
        "form_postal": "郵便番号",
        "form_address": "住所",
        "btn_add_client": "取引先を登録",
        "msg_add_success": "新規取引先が登録されました。",
        "msg_name_required": "取引先名を入力してください。",
    },
    "EN": {
        "page_title": "Client Management",
        "title": "🤝 Client Management",
        "tab1": "🏢 Client List Management",
        "tab2": "➕ Register New Client",
        "sub_tab1": "Registered Client List",
        "btn_save_clients": "💾 Save Client Information",
        "msg_save_success": "Client information has been saved successfully.",
        "msg_no_clients": "No registered clients. Please register a new client.",
        "form_c_name": "Client Name",
        "form_b_type": "Business Type",
        "b_type_options": [
            "Wholesale",
            "Retail",
            "Online",
            "Overseas",
            "Other",
        ],
        "form_c_person": "Contact Person",
        "form_phone": "Phone",
        "form_email": "Email",
        "form_postal": "Postal Code",
        "form_address": "Address",
        "btn_add_client": "Register Client",
        "msg_add_success": "New client has been registered successfully.",
        "msg_name_required": "Please enter the client name.",
    },
}

# 테이블 컬럼 매핑 (내부 DB 표준 key <-> 화면 표시 라벨)
CLIENT_MAPS = {
    "KO": {
        "client_name": "거래처명",
        "business_type": "업태/구분",
        "contact_person": "담당자명",
        "phone": "전화번호",
        "email": "이메일",
        "postal_code": "우편번호",
        "address": "주소",
    },
    "JA": {
        "client_name": "取引先名",
        "business_type": "業態/区分",
        "contact_person": "担当者名",
        "phone": "電話番号",
        "email": "メールアドレス",
        "postal_code": "郵便番号",
        "address": "住所",
    },
    "EN": {
        "client_name": "Client Name",
        "business_type": "Business Type",
        "contact_person": "Contact Person",
        "phone": "Phone",
        "email": "Email",
        "postal_code": "Postal Code",
        "address": "Address",
    },
}

# 2. 현재 선택된 언어 감지 ('lang' 또는 'language' 세션 키 호환 처리)
raw_lang = st.session_state.get("lang") or st.session_state.get("language") or "KO"
lang_mapping = {
    "한국어": "KO",
    "KO": "KO",
    "日本語": "JA",
    "JA": "JA",
    "English": "EN",
    "EN": "EN",
}
current_lang = lang_mapping.get(raw_lang, "KO")

t = TRANSLATIONS[current_lang]
current_col_map = CLIENT_MAPS[current_lang]

# 3. Streamlit 페이지 설정 (최상단 고정)
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 렌더링
render_sidebar()

# 5. 세션 상태 초기화
if "clients" not in st.session_state:
    st.session_state.clients = []

# 6. 메인 타이틀
st.title(t["title"])
st.markdown("---")

tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

# --- [TAB 1] 거래처 목록 관리 ---
with tab1:
    st.subheader(t["sub_tab1"])
    if st.session_state.clients:
        df_c = pd.DataFrame(st.session_state.clients)

        # 표시용 컬럼 변경
        df_c_renamed = df_c.rename(columns=current_col_map)

        edited_c = st.data_editor(
            df_c_renamed, num_rows="dynamic", use_container_width=True
        )

        if st.button(t["btn_save_clients"]):
            # 저장 시 원본 데이터베이스 Key 값으로 역매핑
            inv_map = {v: k for k, v in current_col_map.items()}
            st.session_state.clients = edited_c.rename(
                columns=inv_map
            ).to_dict("records")
            st.success(t["msg_save_success"])
            st.rerun()
    else:
        st.info(t["msg_no_clients"])

# --- [TAB 2] 거래처 신규 등록 ---
with tab2:
    with st.form("add_client_form"):
        c1, c2 = st.columns(2)
        with c1:
            c_name = st.text_input(t["form_c_name"])
            b_type = st.selectbox(t["form_b_type"], t["b_type_options"])
            c_person = st.text_input(t["form_c_person"])
            phone = st.text_input(t["form_phone"])
        with c2:
            email = st.text_input(t["form_email"])
            p_code = st.text_input(t["form_postal"])
            address = st.text_input(t["form_address"])

        if st.form_submit_button(t["btn_add_client"]):
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
                st.success(t["msg_add_success"])
                st.rerun()
            else:
                st.error(t["msg_name_required"])
