import streamlit as st

st.set_page_config(page_title="마스터상품 및 집기관리", layout="wide")

import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("📦 마스터 상품 및 집기 자산 관리")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🛒 상품 마스터 관리", "➕ 신규 상품 등록", "🎪 집기 마스터 & 자산 관리"])

# --- TAB 1: 상품 마스터 ---
with tab1:
    st.subheader("등록된 마스터 상품 목록")
    if st.session_state.master_products:
        df_p = pd.DataFrame(st.session_state.master_products)
        edited_df = st.data_editor(df_p, num_rows="dynamic", use_container_width=True)
        if st.button("💾 상품 변경사항 저장"):
            st.session_state.master_products = edited_df.to_dict("records")
            st.success("상품 마스터가 अपडेट 되었습니다.")
            st.rerun()
    else:
        st.info("등록된 상품이 없습니다.")

# --- TAB 2: 신규 상품 등록 ---
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
            supply_price_jpy = st.number_input("공급 단가(엔)", min_value=0, value=1200)
            list_price_jpy = st.number_input("소비자 가(엔)", min_value=0, value=2500)
            memo = st.text_input("비고/메모")

        if st.form_submit_button("상품 등록"):
            if not jan_code or not product_name:
                st.error("JAN 코드와 상품명은 필수입니다.")
            else:
                st.session_state.master_products.append({
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
                })
                st.success("신규 상품이 등록되었습니다.")
                st.rerun()

# --- TAB 3: 집기 마스터 & 자산 관리 (신규 반영) ---
with tab3:
    st.subheader("🎪 집기(POP/매대/디스플레이) 마스터 등록 및 남은 자산 관리")
    st.caption("집기명, 총 제작수량, 입고창고명, 총 제작비를 입력하시면 개당 단가 및 남아있는 집기의 자산 금액이 자동 산출됩니다.")

    with st.form("fix_form"):
        fc1, fc2 = st.columns(2)
        with fc1:
            f_name = st.text_input("집기명 (예: 아크릴 매대 A타입)")
            f_total_qty = st.number_input("제작/입고 수량(개)", min_value=1, value=100)
            f_wh = st.selectbox("입고 창고명", st.session_state.warehouses)
        with fc2:
            f_cost = st.number_input("총 제작비(엔)", min_value=0, value=500000)
            f_rem_qty = st.number_input("현재 잔여 수량(개)", min_value=0, value=100)

        if st.form_submit_button("🎪 집기 등록 및 자산 반영"):
            unit_c = round(f_cost / f_total_qty, 2) if f_total_qty > 0 else 0
            rem_val = round(unit_c * f_rem_qty, 2)

            st.session_state.master_fixtures.append({
                "fixture_name": f_name,
                "total_qty": f_total_qty,
                "remaining_qty": f_rem_qty,
                "warehouse": f_wh,
                "total_cost": f_cost,
                "unit_cost": unit_c,
                "total_remaining_value": rem_val,
            })
            st.success("집기가 등록되었습니다.")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 집기 보유 및 잔여 자산 현황표")
    if st.session_state.master_fixtures:
        df_fix = pd.DataFrame(st.session_state.master_fixtures)
        df_fix.columns = ["집기명", "총 제작수량", "잔여 수량", "입고창고명", "총 제작비(엔)", "1개당 단가(엔)", "총 잔여 자산가치(엔)"]
        st.dataframe(df_fix, use_container_width=True)
    else:
        st.info("등록된 집기 데이터가 없습니다.")
