import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

st.set_page_config(page_title="거래처 관리", layout="wide")
render_sidebar()

st.title("🤝 거래처 관리")
st.markdown("---")

lang = st.session_state.get("lang", "한국어")

# 세션 상태 초기화 (거래처 목록 & 거래처별 공급가 저장소)
if "clients" not in st.session_state:
    st.session_state.clients = []

if "client_prices" not in st.session_state:
    # 구조: { "거래처명": { "JAN코드": 공급가(float), ... }, ... }
    st.session_state.client_prices = {}

CLIENT_MAPS = {
    "한국어": {
        "client_name": "거래처명",
        "business_type": "업태/구분",
        "contact_person": "담당자명",
        "phone": "전화번호",
        "email": "이메일",
        "postal_code": "우편번호",
        "address": "주소",
    },
    "日本語": {
        "client_name": "取引先名",
        "business_type": "業態/区分",
        "contact_person": "担当者名",
        "phone": "電話番号",
        "email": "メールアドレス",
        "postal_code": "郵便番号",
        "address": "住所",
    },
    "English": {
        "client_name": "Client Name",
        "business_type": "Business Type",
        "contact_person": "Contact Person",
        "phone": "Phone",
        "email": "Email",
        "postal_code": "Postal Code",
        "address": "Address",
    },
}

tab1, tab2, tab3 = st.tabs(
    [
        "🏢 거래처 목록 관리",
        "➕ 거래처 신규 등록",
        "🏷️ 거래처별 공급가 설정",
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: 거래처 목록 관리
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("등록된 거래처 현황")
    if st.session_state.clients:
        df_c = pd.DataFrame(st.session_state.clients)
        df_c_renamed = df_c.rename(
            columns=CLIENT_MAPS.get(lang, CLIENT_MAPS["한국어"])
        )
        edited_c = st.data_editor(
            df_c_renamed, num_rows="dynamic", use_container_width=True
        )

        if st.button("💾 거래처 정보 저장", type="primary"):
            inv_map = {
                v: k
                for k, v in CLIENT_MAPS.get(
                    lang, CLIENT_MAPS["한국어"]
                ).items()
            }
            st.session_state.clients = edited_c.rename(
                columns=inv_map
            ).to_dict("records")
            st.success("거래처 정보가 저장되었습니다.")
            st.rerun()
    else:
        st.info("등록된 거래처가 없습니다. [거래처 신규 등록] 탭에서 추가해 주세요.")

# -----------------------------------------------------------------------------
# TAB 2: 거래처 신규 등록
# -----------------------------------------------------------------------------
with tab2:
    with st.form("add_client_form"):
        c1, c2 = st.columns(2)
        with c1:
            c_name = st.text_input("거래처명 *")
            b_type = st.selectbox(
                "구분", ["도매", "소매", "온라인", "해외", "기타"]
            )
            c_person = st.text_input("담당자명")
            phone = st.text_input("전화번호")
        with c2:
            email = st.text_input("이메일")
            p_code = st.text_input("우편번호")
            address = st.text_input("주소")

        if st.form_submit_button("거래처 등록", type="primary"):
            if c_name:
                st.session_state.clients.append(
                    {
                        "client_name": c_name,
                        "business_type": b_type,
                        "contact_person": c_person,
                        "phone": phone,
                        "email": email,
                        "postal_code": p_code,
                        "address": address,
                    }
                )
                st.success(f"신규 거래처 [{c_name}]이(가) 등록되었습니다.")
                st.rerun()
            else:
                st.warning("거래처명은 필수 입력 항목입니다.")

# -----------------------------------------------------------------------------
# TAB 3: 거래처별 공급가(단가) 설정 (신규 추가)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🏷️ 거래처별 전용 공급가 설정")
    st.caption(
        "거래처별로 개별 공급가를 설정해두면 출고 시 자동으로 맞춤 단가가 적용됩니다."
    )

    # 1. 등록된 거래처 목록 가져오기
    client_list = [
        c.get("client_name")
        for c in st.session_state.clients
        if isinstance(c, dict) and c.get("client_name")
    ]

    # 2. 등록된 상품 마스터 가져오기
    products = st.session_state.get("products", [])

    if not client_list:
        st.warning("먼저 [거래처 신규 등록] 탭에서 거래처를 등록해 주세요.")
    elif not products:
        st.warning("상품 마스터에 등록된 상품이 없습니다. 상품 관리 메뉴에서 상품을 먼저 등록해 주세요.")
    else:
        # 거래처 선택 드롭다운
        selected_client = st.selectbox(
            "🔍 공급가를 설정할 거래처를 선택하세요",
            options=client_list,
            key="price_setting_client_select",
        )

        if selected_client:
            st.markdown(f"#### 📋 **[{selected_client}]** 거래처 단가 설정표")

            # 기존 저장된 단가 가져오기
            existing_prices = st.session_state.client_prices.get(
                selected_client, {}
            )

            # 상품 마스터 데이터를 기반으로 편집용 데이터프레임 생성
            price_table_data = []
            for p in products:
                jan = p.get("jan_code") or p.get("product_code", "")
                p_name = p.get("product_name", "")

                # 기본 판매 단가 (기본값)
                default_price = float(
                    p.get("selling_price", p.get("unit_price", 0))
                )

                # 기존 설정된 전용 공급가가 있다면 사용, 없으면 기본 판매단가 사용
                custom_price = float(existing_prices.get(jan, default_price))

                price_table_data.append(
                    {
                        "JAN코드": jan,
                        "상품명": p_name,
                        "마스터 기본 단가": default_price,
                        "거래처 공급가 (엔)": custom_price,
                    }
                )

            df_price_setting = pd.DataFrame(price_table_data)

            # 단가 수정용 Data Editor
            edited_price_df = st.data_editor(
                df_price_setting,
                use_container_width=True,
                column_config={
                    "JAN코드": st.column_config.TextColumn("JAN코드", disabled=True),
                    "상품명": st.column_config.TextColumn("상품명", disabled=True),
                    "마스터 기본 단가": st.column_config.NumberColumn(
                        "마스터 기본 단가", format="¥%d", disabled=True
                    ),
                    "거래처 공급가 (엔)": st.column_config.NumberColumn(
                        "거래처 공급가 (엔)",
                        help="해당 거래처에 적용할 전용 공급가를 입력하세요.",
                        min_value=0,
                        step=10,
                        format="¥%d",
                    ),
                },
                disabled=["JAN코드", "상품명", "마스터 기본 단가"],
                key=f"editor_{selected_client}",
            )

            # 저장 버튼
            if st.button(
                f"💾 [{selected_client}] 공급가 설정 저장", type="primary"
            ):
                # 단가 dictionary 생성 { "JAN코드": 공급가 }
                new_price_map = {}
                for row in edited_price_df.to_dict("records"):
                    jan_code = row["JAN코드"]
                    custom_val = float(row["거래처 공급가 (엔)"])
                    new_price_map[jan_code] = custom_val

                # 세션에 저장
                st.session_state.client_prices[selected_client] = new_price_map
                st.success(
                    f"[{selected_client}] 거래처의 상품별 공급가가 성공적으로 저장되었습니다!"
                )
                st.rerun()
