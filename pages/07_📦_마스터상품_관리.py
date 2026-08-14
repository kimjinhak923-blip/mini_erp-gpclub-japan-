import streamlit as st

st.set_page_config(page_title="마스터상품 관리", layout="wide")

import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

st.title("📦 마스터 상품 및 집기 자산 관리")
st.markdown("---")

lang = st.session_state.get("lang", "한국어")

# 다국어 컬럼 맵핑
COLUMN_MAPS = {
    "한국어": {
        "jan_code": "JAN 코드 (바코드)",
        "product_name": "상품명",
        "category": "카테고리",
        "capacity": "용량/규격",
        "units_per_box": "박스당 입수량(EA)",
        "box_cbm": "박스 CBM",
        "box_weight_kg": "박스 중량(kg)",
        "plt_qty": "PLT당 박스 수",
        "supply_price_jpy": "공급 단가(엔)",
        "list_price_jpy": "소비자 가(엔)",
        "memo": "비고/메모"
    },
    "日本語": {
        "jan_code": "JANコード",
        "product_name": "商品名",
        "category": "カテゴリー",
        "capacity": "容量/規格",
        "units_per_box": "1箱の入数(EA)",
        "box_cbm": "箱 CBM",
        "box_weight_kg": "箱 重量(kg)",
        "plt_qty": "PLT当り箱数",
        "supply_price_jpy": "供給単価(円)",
        "list_price_jpy": "上代(円)",
        "memo": "備考/メモ"
    },
    "English": {
        "jan_code": "JAN Code",
        "product_name": "Product Name",
        "category": "Category",
        "capacity": "Capacity",
        "units_per_box": "Units Per Box",
        "box_cbm": "Box CBM",
        "box_weight_kg": "Box Weight(kg)",
        "plt_qty": "Boxes Per PLT",
        "supply_price_jpy": "Supply Price (JPY)",
        "list_price_jpy": "List Price (JPY)",
        "memo": "Memo"
    }
}

tab1, tab2, tab3 = st.tabs(["🛒 상품 마스터 관리", "➕ 신규 상품 등록", "🎪 집기 마스터 & 자산 관리"])

with tab1:
    st.subheader("등록된 마스터 상품 목록")
    if st.session_state.master_products:
        df_p = pd.DataFrame(st.session_state.master_products)
        # 선택된 언어에 따른 컬럼명 변경
        df_p_renamed = df_p.rename(columns=COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"]))
        edited_df = st.data_editor(df_p_renamed, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 상품 변경사항 저장"):
            # 원래 파이썬 세션 키값으로 다시 복원하여 저장
            inv_map = {v: k for k, v in COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"]).items()}
            st.session_state.master_products = edited_df.rename(columns=inv_map).to_dict("records")
            st.success("상품 마스터가 성공적으로 저장되었습니다.")
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

with tab3:
    st.subheader("🎪 집기 마스터 & 자산 관리")
    with st.form("fix_form"):
        fc1, fc2 = st.columns(2)
        with fc1:
            f_name = st.text_input("집기명")
            f_total_qty = st.number_input("제작/입고 수량(개)", min_value=1, value=100)
            f_wh = st.selectbox("입고 창고명", st.session_state.warehouses)
        with fc2:
            f_cost = st.number_input("총 제작비(엔)", min_value=0, value=500000)
            f_rem_qty = st.number_input("현재 잔여 수량(개)", min_value=0, value=100)

        if st.form_submit_button("🎪 집기 등록"):
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

    if st.session_state.master_fixtures:
        df_fix = pd.DataFrame(st.session_state.master_fixtures)
        st.dataframe(df_fix, use_container_width=True)
