import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# 1. 다국어 딕셔너리 정의 (한국어 / 일본어 / 영어)
TRANSLATIONS = {
    "KO": {
        "page_title": "마스터상품 관리",
        "title": "📦 마스터 상품 및 집기 자산 관리",
        "tab1": "🛒 상품 마스터 관리",
        "tab2": "➕ 신규 상품 등록",
        "tab3": "🎪 집기 마스터 & 자산 관리",
        # Tab 1
        "sub_tab1": "등록된 마스터 상품 목록",
        "btn_save_products": "💾 상품 변경사항 저장",
        "msg_save_success": "상품 마스터가 성공적으로 저장되었습니다.",
        "msg_no_products": "등록된 상품이 없습니다.",
        # Tab 2
        "sub_tab2": "신규 상품 입력",
        "label_box_jan": "단상자 JAN 코드 (곽/박스 바코드)",
        "ph_box_jan": "예: 4580000000001",
        "label_single_jan": "낱장 JAN 코드 (마스크팩 등 필요시)",
        "ph_single_jan": "선택 사항",
        "label_p_name": "상품명",
        "label_cat": "카테고리",
        "val_cat_default": "스킨케어",
        "label_capa": "용량/규격",
        "val_capa_default": "50ml",
        "label_units_box": "박스당 입수량(EA)",
        "label_box_cbm": "박스 CBM",
        "label_box_weight": "박스 중량(kg)",
        "label_plt_qty": "PLT당 박스 수",
        "label_supply_price": "공급 단가(엔)",
        "label_list_price": "소비자 가(엔)",
        "label_memo": "비고/메모",
        "btn_add_product": "상품 등록",
        "msg_err_required": "단상자 JAN 코드와 상품명은 필수입니다.",
        "msg_add_success": "신규 상품이 등록되었습니다.",
        # Tab 3
        "sub_tab3_1": "🎪 집기 마스터 & 자산 관리",
        "label_f_name": "집기명",
        "label_f_qty": "제작/입고 수량(개)",
        "label_f_cost": "제작비(엔)",
        "label_f_wh": "입고 창고명",
        "btn_add_fixture": "🎪 집기 등록",
        "msg_fix_success": "[{}] 집기가 등록되었습니다.",
        "msg_fix_err": "집기명을 입력해 주세요.",
        "sub_tab3_2": "##### 📊 집기 자산 및 잔여 현황 (출고 반영 자동 계산)",
        "msg_no_fixtures": "등록된 집기 자산이 없습니다.",
        # Fixture Table Headers
        "col_fix_name": "집기명",
        "col_fix_wh": "입고 창고",
        "col_fix_init_qty": "최초 제작수량",
        "col_fix_out_qty": "출고 누적수량",
        "col_fix_rem_qty": "현재 잔여수량",
        "col_fix_total_cost": "총 제작비 (엔)",
        "col_fix_unit_cost": "개당 제작단가 (엔)",
        "col_fix_rem_val": "잔여 자산가치 (엔)",
        "unit_pcs": "개",
    },
    "JA": {
        "page_title": "マスター商品管理",
        "title": "📦 マスター商品および什器資産管理",
        "tab1": "🛒 상품 마스터 관리",
        "tab2": "➕ 新規商品登録",
        "tab3": "🎪 什器マスター&資産管理",
        "sub_tab1": "登録済みマスター商品一覧",
        "btn_save_products": "💾 商品の変更事項を保存",
        "msg_save_success": "商品マスターが正常に保存されました。",
        "msg_no_products": "登録された商品がありません。",
        "sub_tab2": "新規商品入力",
        "label_box_jan": "化粧箱 JANコード (箱バーコード)",
        "ph_box_jan": "例: 4580000000001",
        "label_single_jan": "単品 JANコード (シートマスク等任意)",
        "ph_single_jan": "任意項目",
        "label_p_name": "商品名",
        "label_cat": "カテゴリー",
        "val_cat_default": "スキンケア",
        "label_capa": "容量/規格",
        "val_capa_default": "50ml",
        "label_units_box": "1箱の入数(EA)",
        "label_box_cbm": "箱 CBM",
        "label_box_weight": "箱 重量(kg)",
        "label_plt_qty": "PLT当り箱数",
        "label_supply_price": "供給単価(円)",
        "label_list_price": "上代(円)",
        "label_memo": "備考/メモ",
        "btn_add_product": "商品を登録",
        "msg_err_required": "化粧箱 JANコードと商品名は必須です。",
        "msg_add_success": "新規商品が登録されました。",
        "sub_tab3_1": "🎪 什器マスター&資産管理",
        "label_f_name": "什器名",
        "label_f_qty": "制作/入庫数量(個)",
        "label_f_cost": "制作費(円)",
        "label_f_wh": "入庫倉庫名",
        "btn_add_fixture": "🎪 什器を登録",
        "msg_fix_success": "[{}] 什器が登録されました。",
        "msg_fix_err": "什器名を入力してください。",
        "sub_tab3_2": "##### 📊 什器資産および残高状況 (出荷反映自動計算)",
        "msg_no_fixtures": "登録された什器資産がありません。",
        "col_fix_name": "什器名",
        "col_fix_wh": "入庫倉庫",
        "col_fix_init_qty": "初回制作数量",
        "col_fix_out_qty": "出荷累計数量",
        "col_fix_rem_qty": "現在残高数量",
        "col_fix_total_cost": "総制作費 (円)",
        "col_fix_unit_cost": "1個当り制作単価 (円)",
        "col_fix_rem_val": "残高資産価値 (円)",
        "unit_pcs": "個",
    },
    "EN": {
        "page_title": "Master Product Management",
        "title": "📦 Master Product & Fixture Asset Management",
        "tab1": "🛒 Product Master Management",
        "tab2": "➕ Register New Product",
        "tab3": "🎪 Fixture Master & Assets",
        "sub_tab1": "Registered Master Product List",
        "btn_save_products": "💾 Save Product Changes",
        "msg_save_success": "Product master saved successfully.",
        "msg_no_products": "No registered products.",
        "sub_tab2": "Enter New Product Information",
        "label_box_jan": "Box JAN Code",
        "ph_box_jan": "Ex: 4580000000001",
        "label_single_jan": "Single Unit JAN Code (Opt)",
        "ph_single_jan": "Optional",
        "label_p_name": "Product Name",
        "label_cat": "Category",
        "val_cat_default": "Skincare",
        "label_capa": "Capacity/Spec",
        "val_capa_default": "50ml",
        "label_units_box": "Units Per Box (EA)",
        "label_box_cbm": "Box CBM",
        "label_box_weight": "Box Weight (kg)",
        "label_plt_qty": "Boxes Per PLT",
        "label_supply_price": "Supply Price (JPY)",
        "label_list_price": "List Price (JPY)",
        "label_memo": "Memo",
        "btn_add_product": "Register Product",
        "msg_err_required": "Box JAN Code and Product Name are required.",
        "msg_add_success": "New product registered successfully.",
        "sub_tab3_1": "🎪 Fixture Master & Asset Management",
        "label_f_name": "Fixture Name",
        "label_f_qty": "Production/Inbound Qty",
        "label_f_cost": "Production Cost (JPY)",
        "label_f_wh": "Inbound Warehouse",
        "btn_add_fixture": "🎪 Register Fixture",
        "msg_fix_success": "[{}] fixture registered successfully.",
        "msg_fix_err": "Please enter fixture name.",
        "sub_tab3_2": "##### 📊 Fixture Assets & Remaining Status (Auto-calculated from Outbound)",
        "msg_no_fixtures": "No registered fixture assets.",
        "col_fix_name": "Fixture Name",
        "col_fix_wh": "Inbound WH",
        "col_fix_init_qty": "Initial Qty",
        "col_fix_out_qty": "Cumulative Outbound",
        "col_fix_rem_qty": "Current Remaining",
        "col_fix_total_cost": "Total Cost (JPY)",
        "col_fix_unit_cost": "Unit Cost (JPY)",
        "col_fix_rem_val": "Remaining Asset Value (JPY)",
        "unit_pcs": "pcs",
    },
}

# 테이블 컬럼 매핑 (내부 DB 표준 key <-> 화면 표시 라벨)
COLUMN_MAPS = {
    "KO": {
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
    "JA": {
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
    "EN": {
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
current_col_map = COLUMN_MAPS[current_lang]

# 3. Streamlit 페이지 설정 (최상단 고정)
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 렌더링
render_sidebar()

# 5. 세션 상태 초기화
if "master_products" not in st.session_state:
    st.session_state.master_products = []
if "master_fixtures" not in st.session_state:
    st.session_state.master_fixtures = []

# 6. 메인 타이틀
st.title(t["title"])
st.markdown("---")

tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

# --- [TAB 1] 상품 마스터 관리 ---
with tab1:
    st.subheader(t["sub_tab1"])
    if st.session_state.master_products:
        df_p = pd.DataFrame(st.session_state.master_products)

        if "jan_code" in df_p.columns and "box_jan_code" not in df_p.columns:
            df_p.rename(columns={"jan_code": "box_jan_code"}, inplace=True)
        if "single_jan_code" not in df_p.columns:
            df_p["single_jan_code"] = ""

        df_p_renamed = df_p.rename(columns=current_col_map)
        edited_df = st.data_editor(
            df_p_renamed, num_rows="dynamic", use_container_width=True
        )

        if st.button(t["btn_save_products"]):
            inv_map = {v: k for k, v in current_col_map.items()}
            st.session_state.master_products = edited_df.rename(
                columns=inv_map
            ).to_dict("records")
            st.success(t["msg_save_success"])
            st.rerun()
    else:
        st.info(t["msg_no_products"])

# --- [TAB 2] 신규 상품 등록 ---
with tab2:
    st.subheader(t["sub_tab2"])
    with st.form("add_product_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            box_jan_code = st.text_input(
                t["label_box_jan"], placeholder=t["ph_box_jan"]
            )
            single_jan_code = st.text_input(
                t["label_single_jan"], placeholder=t["ph_single_jan"]
            )
            product_name = st.text_input(t["label_p_name"])
            category = st.text_input(
                t["label_cat"], value=t["val_cat_default"]
            )
            capacity = st.text_input(
                t["label_capa"], value=t["val_capa_default"]
            )
        with col2:
            units_per_box = st.number_input(
                t["label_units_box"], min_value=1, value=24
            )
            box_cbm = st.number_input(
                t["label_box_cbm"],
                min_value=0.0,
                value=0.02,
                format="%.3f",
            )
            box_weight_kg = st.number_input(
                t["label_box_weight"], min_value=0.0, value=10.0
            )
            plt_qty = st.number_input(
                t["label_plt_qty"], min_value=1, value=40
            )
        with col3:
            supply_price_jpy = st.number_input(
                t["label_supply_price"], min_value=0, value=1200
            )
            list_price_jpy = st.number_input(
                t["label_list_price"], min_value=0, value=2500
            )
            memo = st.text_input(t["label_memo"])

        if st.form_submit_button(t["btn_add_product"]):
            if not box_jan_code or not product_name:
                st.error(t["msg_err_required"])
            else:
                st.session_state.master_products.append({
                    "jan_code": box_jan_code,
                    "box_jan_code": box_jan_code,
                    "single_jan_code": (
                        single_jan_code if single_jan_code else "-"
                    ),
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
                st.success(t["msg_add_success"])
                st.rerun()

# --- [TAB 3] 집기 마스터 & 자산 관리 ---
with tab3:
    st.subheader(t["sub_tab3_1"])

    with st.form("fix_form"):
        fc1, fc2 = st.columns(2)
        with fc1:
            f_name = st.text_input(t["label_f_name"])
            f_total_qty = st.number_input(
                t["label_f_qty"], min_value=1, value=100
            )
        with fc2:
            f_cost = st.number_input(
                t["label_f_cost"], min_value=0, value=500000
            )
            f_wh = st.selectbox(
                t["label_f_wh"],
                st.session_state.get(
                    "warehouses", ["SAGAWA", "L&K", "大吉商事"]
                ),
            )

        if st.form_submit_button(t["btn_add_fixture"]):
            if f_name:
                unit_c = (
                    round(f_cost / f_total_qty, 2) if f_total_qty > 0 else 0
                )
                st.session_state.master_fixtures.append({
                    "fixture_name": f_name,
                    "total_qty": f_total_qty,
                    "warehouse": f_wh,
                    "total_cost": f_cost,
                    "unit_cost": unit_c,
                })
                st.success(t["msg_fix_success"].format(f_name))
                st.rerun()
            else:
                st.error(t["msg_fix_err"])

    st.markdown("---")
    st.write(t["sub_tab3_2"])

    if st.session_state.master_fixtures:
        logs = st.session_state.get("stock_logs", [])
        fixtures_display = []

        for fix in st.session_state.master_fixtures:
            f_name = fix["fixture_name"]
            total_q = fix["total_qty"]

            # 출고 이력 중 해당 집기 출고량 자동 합산 및 차감 (내부 연산 기준 동일 유지)
            out_q = sum(
                l.get("qty", 0)
                for l in logs
                if l.get("product_name") == f_name
                and l.get("type") == "출고"
                and l.get("item_category") == "집기"
            )
            calc_rem_q = max(0, total_q - out_q)
            unit_c = fix.get(
                "unit_cost",
                round(fix["total_cost"] / total_q, 2) if total_q > 0 else 0,
            )
            rem_value = round(unit_c * calc_rem_q, 2)

            # 화면 표시는 동적 다국어 처리
            fixtures_display.append({
                t["col_fix_name"]: f_name,
                t["col_fix_wh"]: fix["warehouse"],
                t["col_fix_init_qty"]: f"{total_q:,} {t['unit_pcs']}",
                t["col_fix_out_qty"]: f"{out_q:,} {t['unit_pcs']}",
                t["col_fix_rem_qty"]: f"{calc_rem_q:,} {t['unit_pcs']}",
                t["col_fix_total_cost"]: f"¥{fix['total_cost']:,.0f}",
                t["col_fix_unit_cost"]: f"¥{unit_c:,.2f}",
                t["col_fix_rem_val"]: f"¥{rem_value:,.0f}",
            })

        st.dataframe(
            pd.DataFrame(fixtures_display), use_container_width=True
        )
    else:
        st.info(t["msg_no_fixtures"])
