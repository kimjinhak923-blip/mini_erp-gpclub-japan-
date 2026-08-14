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
    # 구조: { "거래처명": { "JAN코드": { "product_name": ..., "capacity": ..., "list_price": ..., "supply_price": ..., "supply_rate": ... } } }
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
# TAB 3: 거래처별 공급가(단가) 및 공급률 설정
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🏷️ 거래처별 전용 공급가 & 공급률 설정")
    st.caption(
        "거래처와 상품을 선택하면 소비자가 및 용량이 자동 입력되며, 공급가를 설정하여 공급률을 자동 계산 등록할 수 있습니다."
    )

    # 1. 등록된 거래처 목록 가져오기
    client_list = [
        c.get("client_name")
        for c in st.session_state.clients
        if isinstance(c, dict) and c.get("client_name")
    ]

    # 2. 등록된 상품 마스터 가져오기 (master_products 및 products 지원)
    products = st.session_state.get(
        "master_products", st.session_state.get("products", [])
    )

    if not client_list:
        st.warning("먼저 [거래처 신규 등록] 탭에서 거래처를 등록해 주세요.")
    elif not products:
        st.warning("상품 마스터에 등록된 상품이 없습니다. 마스터 상품 관리 메뉴에서 상품을 먼저 등록해 주세요.")
    else:
        # 거래처 및 상품 선택 섹션
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            selected_client = st.selectbox(
                "🏢 1. 거래처 선택",
                options=client_list,
                key="sel_client_price",
            )

        # 상품 맵 생성
        prod_dict = {}
        prod_options = []
        for p in products:
            jan = p.get("box_jan_code") or p.get("jan_code") or p.get("product_code", "")
            p_name = p.get("product_name", "")
            label = f"{p_name} [{jan}]" if jan else p_name
            prod_dict[label] = p
            prod_options.append(label)

        with c_col2:
            selected_prod_label = st.selectbox(
                "📦 2. 상품 선택",
                options=prod_options,
                key="sel_prod_price",
            )

        # 선택된 상품 정보 추출
        selected_p = prod_dict[selected_prod_label]
        jan_code = selected_p.get("box_jan_code") or selected_p.get("jan_code", "")
        product_name = selected_p.get("product_name", "")
        capacity = selected_p.get("capacity", "-")
        list_price = float(
            selected_p.get("list_price_jpy_excl_tax", selected_p.get("list_price_jpy", 0))
        )

        st.markdown("---")
        st.markdown(f"##### 📝 **[{selected_client}]** 거래처에 적용할 **[{product_name}]** 공급가 설정")

        # 기존 설정 정보 확인
        client_existing_prices = st.session_state.client_prices.get(selected_client, {})
        existing_info = client_existing_prices.get(jan_code, {})
        
        # 기본 공급가 설정 (기존 등록값이 있으면 사용, 없으면 소비자가의 50%를 기본값으로 지정)
        if existing_info and "supply_price" in existing_info:
            default_sp = float(existing_info["supply_price"])
        else:
            default_sp = float(list_price * 0.5) if list_price > 0 else 0.0

        # 상세 입력 폼 (자동 입력 / 수동 입력 / 자동 계산)
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            st.text_input("용량/규격 (자동)", value=str(capacity), disabled=True)

        with col_p2:
            st.text_input("소비자 가 (엔, 세외) (자동)", value=f"¥{int(list_price):,}", disabled=True)

        with col_p3:
            supply_price = st.number_input(
                "공급가 입력 (엔 ¥) *",
                min_value=0,
                value=int(default_sp),
                step=50,
                key=f"sp_input_{selected_client}_{jan_code}",
            )

        with col_p4:
            # 공급률 자동 계산 (%) = (공급가 / 소비자가) * 100
            supply_rate = round((supply_price / list_price) * 100, 2) if list_price > 0 else 0.0
            st.text_input("공급률 (자동계산)", value=f"{supply_rate:.2f}%", disabled=True)

        # 등록 저장 버튼
        if st.button("💾 공급가 & 공급률 등록/업데이트", type="primary"):
            if selected_client not in st.session_state.client_prices:
                st.session_state.client_prices[selected_client] = {}

            st.session_state.client_prices[selected_client][jan_code] = {
                "jan_code": jan_code,
                "product_name": product_name,
                "capacity": capacity,
                "list_price": list_price,
                "supply_price": float(supply_price),
                "supply_rate": supply_rate,
            }

            st.success(
                f"[{selected_client}] 거래처에 [{product_name}] 공급가 ¥{int(supply_price):,} (공급률 {supply_rate:.2f}%) 설정이 완료되었습니다!"
            )
            st.rerun()

        # -----------------------------------------------------------------------------
        # 선택된 거래처의 전체 등록 공급가 목록 출력 및 수정
        # -----------------------------------------------------------------------------
        st.markdown("---")
        st.markdown(f"#### 📊 **[{selected_client}]** 거래처 전용 단가표 현황")

        current_prices = st.session_state.client_prices.get(selected_client, {})

        if current_prices:
            table_rows = []
            for j_code, item in current_prices.items():
                l_price = float(item.get("list_price", 0))
                s_price = float(item.get("supply_price", 0))
                s_rate = round((s_price / l_price * 100), 2) if l_price > 0 else 0.0

                table_rows.append(
                    {
                        "JAN코드": j_code,
                        "상품명": item.get("product_name", ""),
                        "용량/규격": item.get("capacity", "-"),
                        "소비자 가(엔)": l_price,
                        "공급가(엔)": s_price,
                        "공급률(%)": s_rate,
                    }
                )

            df_prices = pd.DataFrame(table_rows)

            edited_price_df = st.data_editor(
                df_prices,
                use_container_width=True,
                column_config={
                    "JAN코드": st.column_config.TextColumn("JAN코드", disabled=True),
                    "상품명": st.column_config.TextColumn("상품명", disabled=True),
                    "용량/규격": st.column_config.TextColumn("용량/규격", disabled=True),
                    "소비자 가(엔)": st.column_config.NumberColumn(
                        "소비자 가(엔)", format="¥%d", disabled=True
                    ),
                    "공급가(엔)": st.column_config.NumberColumn(
                        "공급가(엔)", format="¥%d", help="공급가를 수정하면 저장 시 공급률이 자동 재계산됩니다."
                    ),
                    "공급률(%)": st.column_config.NumberColumn(
                        "공급률(%)", format="%.2f%%", disabled=True
                    ),
                },
                key=f"editor_table_{selected_client}",
            )

            if st.button(f"💾 [{selected_client}] 단가표 변경사항 저장"):
                for row in edited_price_df.to_dict("records"):
                    j_c = row["JAN코드"]
                    s_p = float(row["공급가(엔)"])
                    l_p = float(row["소비자 가(엔)"])
                    s_r = round((s_p / l_p * 100), 2) if l_p > 0 else 0.0

                    if j_c in st.session_state.client_prices[selected_client]:
                        st.session_state.client_prices[selected_client][j_c]["supply_price"] = s_p
                        st.session_state.client_prices[selected_client][j_c]["supply_rate"] = s_r

                st.success(f"[{selected_client}] 거래처의 공급가 수정사항이 업데이트되었습니다.")
                st.rerun()
        else:
            st.info(
                f"[{selected_client}] 거래처에 등록된 상품 전용 공급가가 없습니다. 위 메뉴에서 상품을 선택해 등록해 주세요."
            )
