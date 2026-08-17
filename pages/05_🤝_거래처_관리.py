import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar

st.set_page_config(page_title="거래처 관리", layout="wide")
render_sidebar()

# DB 테이블 초기화
db.init_db()

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
# TAB 1: 거래처 목록 관리 (수정 / 선택 삭제 기능 추가)
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("등록된 거래처 현황")
    
    # DB에서 거래처 목록 불러오기
    clients = db.load_clients()

    if clients:
        df_c = pd.DataFrame(clients)
        
        # 선택 삭제용 체크박스 칼럼 추가
        df_c["선택"] = False

        # 칼럼 순서 정렬 ("선택" 칼럼을 가장 앞으로)
        target_cols = [
            "선택",
            "client_name",
            "business_type",
            "contact_person",
            "phone",
            "email",
            "postal_code",
            "address",
        ]
        existing_cols = [c for c in target_cols if c in df_c.columns]
        df_c_filtered = df_c[existing_cols]

        # 다국어 맵핑
        mapping_dict = CLIENT_MAPS.get(lang, CLIENT_MAPS["한국어"]).copy()
        mapping_dict["선택"] = "선택"
        df_c_renamed = df_c_filtered.rename(columns=mapping_dict)

        edited_c = st.data_editor(
            df_c_renamed,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", help="삭제할 거래처를 체크하세요.", default=False),
            },
            key="client_list_editor",
        )

        btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 5])

        # 1. 수정사항 저장 버튼
        with btn_col1:
            if st.button("💾 거래처 정보 저장", type="primary", use_container_width=True):
                save_df = edited_c.drop(columns=["선택"], errors="ignore")
                inv_map = {
                    v: k
                    for k, v in CLIENT_MAPS.get(
                        lang, CLIENT_MAPS["한국어"]
                    ).items()
                }
                updated_clients = save_df.rename(columns=inv_map).to_dict("records")
                
                # DB 저장
                db.save_clients(updated_clients)
                st.success("거래처 정보가 DB에 저장되었습니다.")
                st.rerun()

        # 2. 선택 항목 삭제 버튼
        with btn_col2:
            if st.button("🗑️ 선택한 거래처 삭제", type="secondary", use_container_width=True):
                selected_rows = edited_c[edited_c["선택"] == True]

                if selected_rows.empty:
                    st.warning("삭제할 거래처를 목록에서 먼저 체크해 주세요.")
                else:
                    remaining_df = edited_c[edited_c["선택"] == False].drop(columns=["선택"], errors="ignore")
                    inv_map = {
                        v: k
                        for k, v in CLIENT_MAPS.get(
                            lang, CLIENT_MAPS["한국어"]
                        ).items()
                    }
                    updated_clients = remaining_df.rename(columns=inv_map).to_dict("records")

                    # DB 저장
                    db.save_clients(updated_clients)
                    st.success(f"{len(selected_rows)}개 거래처가 성공적으로 삭제되었습니다.")
                    st.rerun()
    else:
        st.info("등록된 거래처가 없습니다. [거래처 신규 등록] 탭에서 추가해 주세요.")

# -----------------------------------------------------------------------------
# TAB 2: 거래처 신규 등록 (StreamlitAPIException 수정 적용)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("신규 거래처 등록")

    # st.form() 객체를 변수로 할당하여 사용
    client_form = st.form("add_client_form", clear_on_submit=True)
    
    with client_form:
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

        # st.form_submit_button 대신 client_form.form_submit_button 사용
        submitted = client_form.form_submit_button("거래처 등록", type="primary")

    if submitted:
        if c_name:
            current_clients = db.load_clients()
            
            # 거래처명 중복 확인
            existing_names = [c.get("client_name") for c in current_clients]
            if c_name in existing_names:
                st.error(f"[{c_name}]은(는) 이미 등록된 거래처입니다.")
            else:
                new_client = {
                    "client_name": c_name,
                    "business_type": b_type,
                    "contact_person": c_person,
                    "phone": phone,
                    "email": email,
                    "postal_code": p_code,
                    "address": address,
                }
                current_clients.append(new_client)
                db.save_clients(current_clients)

                st.success(f"신규 거래처 [{c_name}]이(가) 등록되었습니다.")
                st.rerun()
        else:
            st.warning("거래처명은 필수 입력 항목입니다.")

# -----------------------------------------------------------------------------
# TAB 3: 거래처별 공급가(단가) 및 공급률 설정 (마스터 상품 DB 연동)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🏷️ 거래처별 전용 공급가 & 공급률 설정")
    st.caption(
        "마스터 상품에 등록된 제품을 선택하면 소비자가 및 용량이 자동 입력되며, 공급가를 설정하여 공급률을 자동 계산 등록할 수 있습니다."
    )

    # 1. DB에서 거래처 및 마스터 상품 목록 불러오기
    clients_db = db.load_clients()
    products_db = db.load_products()
    client_prices_db = db.load_client_prices()

    client_list = [c.get("client_name") for c in clients_db if c.get("client_name")]

    if not client_list:
        st.warning("먼저 [거래처 신규 등록] 탭에서 거래처를 등록해 주세요.")
    elif not products_db:
        st.warning("상품 마스터에 등록된 상품이 없습니다. '마스터 상품 관리' 메뉴에서 상품을 먼저 등록해 주세요.")
    else:
        # 거래처 및 상품 선택 섹션
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            selected_client = st.selectbox(
                "🏢 1. 거래처 선택",
                options=client_list,
                key="sel_client_price",
            )

        # 마스터 상품 맵 생성
        prod_dict = {}
        prod_options = []
        for p in products_db:
            jan = p.get("box_jan_code") or p.get("jan_code") or p.get("single_jan_code", "")
            p_name = p.get("product_name", "")
            label = f"{p_name} [{jan}]" if jan and jan != "-" else p_name
            prod_dict[label] = p
            prod_options.append(label)

        with c_col2:
            selected_prod_label = st.selectbox(
                "📦 2. 상품 선택 (마스터 상품 연동)",
                options=prod_options,
                key="sel_prod_price",
            )

        # 선택된 상품 정보 추출
        selected_p = prod_dict[selected_prod_label]
        jan_code = selected_p.get("box_jan_code") or selected_p.get("jan_code", "-")
        product_name = selected_p.get("product_name", "")
        capacity = selected_p.get("capacity", "-")
        list_price = float(
            selected_p.get("list_price_jpy_excl_tax", selected_p.get("list_price_jpy", 0))
        )

        st.markdown("---")
        st.markdown(f"##### 📝 **[{selected_client}]** 거래처에 적용할 **[{product_name}]** 공급가 설정")

        # 기존 설정 정보 확인
        client_existing_prices = client_prices_db.get(selected_client, {})
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
            if selected_client not in client_prices_db:
                client_prices_db[selected_client] = {}

            client_prices_db[selected_client][jan_code] = {
                "jan_code": jan_code,
                "product_name": product_name,
                "capacity": capacity,
                "list_price": list_price,
                "supply_price": float(supply_price),
                "supply_rate": supply_rate,
            }

            # DB에 저장
            db.save_client_prices(client_prices_db)

            st.success(
                f"[{selected_client}] 거래처에 [{product_name}] 공급가 ¥{int(supply_price):,} (공급률 {supply_rate:.2f}%) 설정이 저장 되었습니다!"
            )
            st.rerun()

        # -----------------------------------------------------------------------------
        # 선택된 거래처의 전체 등록 공급가 목록 출력 및 수정/삭제
        # -----------------------------------------------------------------------------
        st.markdown("---")
        st.markdown(f"#### 📊 **[{selected_client}]** 거래처 전용 단가표 현황")

        current_prices = client_prices_db.get(selected_client, {})

        if current_prices:
            table_rows = []
            for j_code, item in current_prices.items():
                l_price = float(item.get("list_price", 0))
                s_price = float(item.get("supply_price", 0))
                s_rate = round((s_price / l_price * 100), 2) if l_price > 0 else 0.0

                table_rows.append(
                    {
                        "선택": False,
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
                    "선택": st.column_config.CheckboxColumn("선택", help="삭제할 품목을 체크하세요.", default=False),
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

            p_btn_col1, p_btn_col2, _ = st.columns([1.5, 1.5, 5])

            # 1. 단가표 수정사항 저장
            with p_btn_col1:
                if st.button(f"💾 [{selected_client}] 단가표 변경사항 저장", type="primary"):
                    updated_dict = {}
                    for row in edited_price_df.to_dict("records"):
                        j_c = row["JAN코드"]
                        s_p = float(row["공급가(엔)"])
                        l_p = float(row["소비자 가(엔)"])
                        s_r = round((s_p / l_p * 100), 2) if l_p > 0 else 0.0

                        updated_dict[j_c] = {
                            "jan_code": j_c,
                            "product_name": row["상품명"],
                            "capacity": row["용량/규격"],
                            "list_price": l_p,
                            "supply_price": s_p,
                            "supply_rate": s_r,
                        }

                    client_prices_db[selected_client] = updated_dict
                    db.save_client_prices(client_prices_db)

                    st.success(f"[{selected_client}] 거래처의 공급가 수정사항이 DB에 저장되었습니다.")
                    st.rerun()

            # 2. 선택한 단가 품목 삭제
            with p_btn_col2:
                if st.button("🗑️ 선택한 품목 삭제", type="secondary"):
                    selected_p_rows = edited_price_df[edited_price_df["선택"] == True]

                    if selected_p_rows.empty:
                        st.warning("삭제할 품목을 목록에서 먼저 체크해 주세요.")
                    else:
                        remaining_rows = edited_price_df[edited_price_df["선택"] == False]
                        updated_dict = {}
                        for row in remaining_rows.to_dict("records"):
                            j_c = row["JAN코드"]
                            updated_dict[j_c] = {
                                "jan_code": j_c,
                                "product_name": row["상품명"],
                                "capacity": row["용량/규격"],
                                "list_price": float(row["소비자 가(엔)"]),
                                "supply_price": float(row["공급가(엔)"]),
                                "supply_rate": float(row["공급률(%)"]),
                            }

                        client_prices_db[selected_client] = updated_dict
                        db.save_client_prices(client_prices_db)

                        st.success(f"[{selected_client}] 거래처에서 선택한 {len(selected_p_rows)}개 품목이 삭제되었습니다.")
                        st.rerun()
        else:
            st.info(
                f"[{selected_client}] 거래처에 등록된 상품 전용 공급가가 없습니다. 위 메뉴에서 상품을 선택해 등록해 주세요."
            )
