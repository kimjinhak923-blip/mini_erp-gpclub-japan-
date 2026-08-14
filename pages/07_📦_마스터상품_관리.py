import streamlit as st

st.set_page_config(page_title="마스터상품 관리", layout="wide")

import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

st.title("📦 마스터 상품 및 집기 자산 관리")
st.markdown("---")

lang = st.session_state.get("lang", "한국어")

# 다국어 컬럼 맵핑 (단상자 / 낱장 JAN 구분 추가)
COLUMN_MAPS = {
    "한국어": {
        "box_jan_code": "단상자 JAN (곽)",
        "single_jan_code": "낱장 JAN (선택)",
        "product_name": "상품명",
        "category": "카테고리",
        "capacity": "용량/규격",
        "units_per_box": "박스당 입수량(EA)",
        "box_cbm": "박스 CBM",
        "box_weight_kg": "박스 중량(kg)",
        "plt_qty": "PLT당 박스 수",
        "supply_price_jpy": "공급 단가(엔)",
        "list_price_jpy": "소비자 가(엔)",
        "memo": "비고/메모",
    },
    "日本語": {
        "box_jan_code": "化粧箱 JAN",
        "single_jan_code": "単品 JAN (任意)",
        "product_name": "商品名",
        "category": "カテゴリー",
        "capacity": "容量/規格",
        "units_per_box": "1箱の入数(EA)",
        "box_cbm": "箱 CBM",
        "box_weight_kg": "箱 重量(kg)",
        "plt_qty": "PLT当り箱数",
        "supply_price_jpy": "供給単価(円)",
        "list_price_jpy": "上代(円)",
        "memo": "備考/メモ",
    },
    "English": {
        "box_jan_code": "Box JAN",
        "single_jan_code": "Single Unit JAN (Opt)",
        "product_name": "Product Name",
        "category": "Category",
        "capacity": "Capacity",
        "units_per_box": "Units Per Box",
        "box_cbm": "Box CBM",
        "box_weight_kg": "Box Weight(kg)",
        "plt_qty": "Boxes Per PLT",
        "supply_price_jpy": "Supply Price (JPY)",
        "list_price_jpy": "List Price (JPY)",
        "memo": "Memo",
    },
}

tab1, tab2, tab3 = st.tabs(["🛒 상품 마스터 관리", "➕ 신규 상품 등록", "🎪 집기 마스터 & 자산 관리"])

# ----------------------------------------------------
# [TAB 1] 마스터 상품 목록
# ----------------------------------------------------
with tab1:
    st.subheader("등록된 마스터 상품 목록")
    if st.session_state.master_products:
        df_p = pd.DataFrame(st.session_state.master_products)

        # 기존 jan_code 데이터 하위 호환성 유지 처리
        if "jan_code" in df_p.columns and "box_jan_code" not in df_p.columns:
            df_p.rename(columns={"jan_code": "box_jan_code"}, inplace=True)
        if "single_jan_code" not in df_p.columns:
            df_p["single_jan_code"] = ""

        # 선택된 언어에 따른 컬럼명 변경
        df_p_renamed = df_p.rename(columns=COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"]))
        edited_df = st.data_editor(df_p_renamed, num_rows="dynamic", use_container_width=True)

        if st.button("💾 상품 변경사항 저장"):
            inv_map = {v: k for k, v in COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"]).items()}
            st.session_state.master_products = edited_df.rename(columns=inv_map).to_dict("records")
            st.success("상품 마스터가 성공적으로 저장되었습니다.")
            st.rerun()
    else:
        st.info("등록된 상품이 없습니다.")

# ----------------------------------------------------
# [TAB 2] 신규 상품 등록 (단상자/낱장 바코드 구분 입력)
# ----------------------------------------------------
with tab2:
    st.subheader("신규 상품 입력")
    with st.form("add_product_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            box_jan_code = st.text_input("단상자 JAN 코드 (곽/박스 바코드)", placeholder="예: 4580000000001")
            single_jan_code = st.text_input("낱장 JAN 코드 (마스크팩 등 필요시 입력)", placeholder="선택 사항")
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
            if not box_jan_code or not product_name:
                st.error("단상자 JAN 코드와 상품명은 필수 입력 항목입니다.")
            else:
                st.session_state.master_products.append({
                    "jan_code": box_jan_code,  # 기존 입출고 연동 호환용
                    "box_jan_code": box_jan_code,
                    "single_jan_code": single_jan_code if single_jan_code else "-",
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

# ----------------------------------------------------
# [TAB 3] 집기 마스터 & 자산 관리 (잔여수량 자동 계산)
# ----------------------------------------------------
with tab3:
    st.subheader("🎪 집기 마스터 & 자산 관리")

    # 1. 신규 집기 등록 폼 (4가지 항목만 입력)
    with st.form("fix_form"):
        fc1, fc2 = st.columns(2)
        with fc1:
            f_name = st.text_input("집기명")
            f_total_qty = st.number_input("제작/입고 수량(개)", min_value=1, value=100)
        with fc2:
            f_cost = st.number_input("제작비(엔)", min_value=0, value=500000)
            f_wh = st.selectbox("입고 창고명", st.session_state.get("warehouses", ["SAGAWA", "L&K", "大吉商事"]))

        if st.form_submit_button("🎪 집기 등록"):
            if f_name:
                unit_c = round(f_cost / f_total_qty, 2) if f_total_qty > 0 else 0
                # 잔여수량은 초기 입력 수량으로 시작하고 자동 계산됨
                st.session_state.master_fixtures.append({
                    "fixture_name": f_name,
                    "total_qty": f_total_qty,
                    "remaining_qty": f_total_qty,  # 초기 등록 시 잔여수량 = 전체수량
                    "warehouse": f_wh,
                    "total_cost": f_cost,
                    "unit_cost": unit_c,
                    "total_remaining_value": f_cost,
                })
                st.success(f"[{f_name}] 집기가 등록되었습니다.")
                st.rerun()
            else:
                st.error("집기명을 입력해 주세요.")

    st.markdown("---")
    st.write("##### 📊 집기 자산 및 잔여 현황")

    # 2. 집기 입출고 이력을 기반으로 잔여수량 실시간 자동 업데이트
    if st.session_state.master_fixtures:
        # stock_logs에서 집기 출고/차감 건이 있을 경우 자동으로 차감 계산
        logs = st.session_state.get("stock_logs", [])

        fixtures_display = []
        for fix in st.session_state.master_fixtures:
            f_name = fix["fixture_name"]
            total_q = fix["total_qty"]

            # 출고 처리된 집기 수량 차감 계산
            out_q = sum(
                l.get("qty", 0) for l in logs if l.get("product_name") == f_name and l.get("type") == "출고"
            )
            calc_rem_q = max(0, total_q - out_q)

            unit_c = fix.get("unit_cost", round(fix["total_cost"] / total_q, 2) if total_q > 0 else 0)
            rem_value = round(unit_c * calc_rem_q, 2)

            # 세션 상태 잔여 수량 자동 동기화
            fix["remaining_qty"] = calc_rem_q
            fix["total_remaining_value"] = rem_value

            fixtures_display.append({
                "집기명": f_name,
                "입고 창고": fix["warehouse"],
                "최초 제작수량": f"{total_q:,} 개",
                "현재 잔여수량": f"{calc_rem_q:,} 개",
                "제작비 (엔)": f"¥{fix['total_cost'] distribution if isinstance(fix['total_cost'], str) else fix['total_cost']:,.0f}",
                "개당 단가 (엔)": f"¥{unit_c:,.2f}",
                "잔여 자산가치 (엔)": f"¥{rem_value:,.0f}",
            })

        df_fix_show = pd.DataFrame(fixtures_display)
        st.dataframe(df_fix_show, use_container_width=True)
    else:
        st.info("등록된 집기 자산이 없습니다.")
