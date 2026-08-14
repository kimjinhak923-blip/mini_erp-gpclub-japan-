import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

st.set_page_config(page_title="마스터상품 관리", layout="wide")
render_sidebar()

st.title("📦 마스터 상품 및 집기 자산 관리")
st.markdown("---")

lang = st.session_state.get("lang", "한국어")

# 세션 상태 초기화
if "master_products" not in st.session_state:
    st.session_state.master_products = []

if "master_fixtures" not in st.session_state:
    st.session_state.master_fixtures = []

# 다국어 칼럼 맵핑
COLUMN_MAPS = {
    "한국어": {
        "box_jan_code": "단상자 JAN (곽)",
        "single_jan_code": "낱장 JAN (선택)",
        "product_name": "상품명",
        "category": "카테고리",
        "capacity": "용량/규격",
        "cost_price_krw": "매입단가(원)",
        "list_price_jpy_excl_tax": "소비자 가(엔, 세외)",
        "units_per_box": "BOX 입수량(EA)",
        "single_box_dim": "단상자 규격(W*D*H)",
        "outer_box_dim": "박스 규격(W*D*H)",
    },
    "日本語": {
        "box_jan_code": "化粧箱 JAN",
        "single_jan_code": "単品 JAN (任意)",
        "product_name": "商品名",
        "category": "カテゴリー",
        "capacity": "容量/規格",
        "cost_price_krw": "仕入単価(KRW)",
        "list_price_jpy_excl_tax": "希望小売価格(円・税抜)",
        "units_per_box": "1箱の入数(EA)",
        "single_box_dim": "化粧箱サイズ(W*D*H)",
        "outer_box_dim": "外箱サイズ(W*D*H)",
    },
    "English": {
        "box_jan_code": "Box JAN",
        "single_jan_code": "Single Unit JAN (Opt)",
        "product_name": "Product Name",
        "category": "Category",
        "capacity": "Capacity",
        "cost_price_krw": "Purchase Price (KRW)",
        "list_price_jpy_excl_tax": "List Price (JPY, Excl. Tax)",
        "units_per_box": "Units Per Box",
        "single_box_dim": "Single Box Dim(W*D*H)",
        "outer_box_dim": "Outer Box Dim(W*D*H)",
    },
}

tab1, tab2, tab3 = st.tabs(
    ["🛒 상품 마스터 관리", "➕ 신규 상품 등록", "🎪 집기 마스터 & 자산 관리"]
)

# -----------------------------------------------------------------------------
# TAB 1: 등록된 상품 마스터 목록
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("등록된 마스터 상품 목록")
    if st.session_state.master_products:
        df_p = pd.DataFrame(st.session_state.master_products)

        # 구 버전 데이터 호환성 및 신규 칼럼 기본값 처리
        if "jan_code" in df_p.columns and "box_jan_code" not in df_p.columns:
            df_p.rename(columns={"jan_code": "box_jan_code"}, inplace=True)
        if "single_jan_code" not in df_p.columns:
            df_p["single_jan_code"] = "-"
        if "cost_price_krw" not in df_p.columns:
            df_p["cost_price_krw"] = df_p.get("supply_price_jpy", 0)
        if "list_price_jpy_excl_tax" not in df_p.columns:
            df_p["list_price_jpy_excl_tax"] = df_p.get("list_price_jpy", 0)
        if "single_box_dim" not in df_p.columns:
            df_p["single_box_dim"] = "-"
        if "outer_box_dim" not in df_p.columns:
            df_p["outer_box_dim"] = "-"

        # 필요 칼럼 순서 정렬
        target_cols = [
            "box_jan_code",
            "single_jan_code",
            "product_name",
            "category",
            "capacity",
            "cost_price_krw",
            "list_price_jpy_excl_tax",
            "units_per_box",
            "single_box_dim",
            "outer_box_dim",
        ]
        existing_cols = [c for c in target_cols if c in df_p.columns]
        df_p_filtered = df_p[existing_cols]

        # 칼럼명 변경 (다국어)
        df_p_renamed = df_p_filtered.rename(
            columns=COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"])
        )

        edited_df = st.data_editor(
            df_p_renamed,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "매입단가(원)": st.column_config.NumberColumn(
                    "매입단가(원)", format="₩%d"
                ),
                "소비자 가(엔, 세외)": st.column_config.NumberColumn(
                    "소비자 가(엔, 세외)", format="¥%d"
                ),
                "BOX 입수량(EA)": st.column_config.NumberColumn(
                    "BOX 입수량(EA)", format="%d"
                ),
            },
        )

        if st.button("💾 상품 변경사항 저장", type="primary"):
            inv_map = {
                v: k
                for k, v in COLUMN_MAPS.get(
                    lang, COLUMN_MAPS["한국어"]
                ).items()
            }
            saved_records = edited_df.rename(columns=inv_map).to_dict("records")

            # jan_code 키 동기화 (타 화면 참조용)
            for item in saved_records:
                item["jan_code"] = item.get("box_jan_code", "")

            st.session_state.master_products = saved_records
            st.session_state.products = (
                saved_records  # 전체 시스템 공유용 상품 세션 동기화
            )

            st.success("상품 마스터가 성공적으로 저장되었습니다.")
            st.rerun()
    else:
        st.info("등록된 상품이 없습니다. [신규 상품 등록] 탭에서 등록해 주세요.")

# -----------------------------------------------------------------------------
# TAB 2: 신규 상품 등록
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("신규 상품 입력")
    with st.form("add_product_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            box_jan_code = st.text_input(
                "단상자 JAN 코드 (곽/박스 바코드) *",
                placeholder="예: 4580000000001",
            )
            single_jan_code = st.text_input(
                "낱장 JAN 코드 (마스크팩 등 필요시)",
                placeholder="예: 4580000000002 (선택)",
            )
            product_name = st.text_input("상품명 *")

        with col2:
            category = st.text_input("카테고리", value="스킨케어")
            capacity = st.text_input("용량/규격", value="50ml")
            cost_price_krw = st.number_input(
                "매입단가(원 ₩)", min_value=0, value=10000, step=500
            )
            list_price_jpy_excl_tax = st.number_input(
                "소비자 가 (엔 ¥, VAT 별도)", min_value=0, value=2500, step=100
            )

        with col3:
            units_per_box = st.number_input(
                "BOX 입수량(EA)", min_value=1, value=24
            )
            single_box_dim = st.text_input(
                "단상자 규격 (가로*세로*높이 mm)",
                placeholder="예: 80*80*150 mm",
            )
            outer_box_dim = st.text_input(
                "박스 규격 (가로*세로*높이 mm)",
                placeholder="예: 350*250*300 mm",
            )

        if st.form_submit_button("상품 등록", type="primary"):
            if not box_jan_code or not product_name:
                st.error("단상자 JAN 코드와 상품명은 필수 입력 항목입니다.")
            else:
                new_item = {
                    "jan_code": box_jan_code,
                    "box_jan_code": box_jan_code,
                    "single_jan_code": single_jan_code
                    if single_jan_code
                    else "-",
                    "product_name": product_name,
                    "category": category,
                    "capacity": capacity,
                    "cost_price_krw": cost_price_krw,
                    "list_price_jpy_excl_tax": list_price_jpy_excl_tax,
                    "units_per_box": units_per_box,
                    "single_box_dim": single_box_dim
                    if single_box_dim
                    else "-",
                    "outer_box_dim": outer_box_dim if outer_box_dim else "-",
                }

                st.session_state.master_products.append(new_item)

                # 다른 페이지 공유용 동기화
                if "products" not in st.session_state:
                    st.session_state.products = []
                st.session_state.products.append(new_item)

                st.success(f"신규 상품 [{product_name}]이(가) 등록되었습니다.")
                st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: 집기 마스터 & 자산 관리
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🎪 집기 마스터 & 자산 관리")

    with st.form("fix_form"):
        fc1, fc2 = st.columns(2)
        with fc1:
            f_name = st.text_input("집기명")
            f_total_qty = st.number_input(
                "제작/입고 수량(개)", min_value=1, value=100
            )
        with fc2:
            f_cost = st.number_input("제작비(엔)", min_value=0, value=500000)
            f_wh = st.selectbox(
                "입고 창고명",
                st.session_state.get(
                    "warehouses", ["SAGAWA", "L&K", "大吉商事"]
                ),
            )

        if st.form_submit_button("🎪 집기 등록", type="primary"):
            if f_name:
                unit_c = (
                    round(f_cost / f_total_qty, 2) if f_total_qty > 0 else 0
                )
                st.session_state.master_fixtures.append(
                    {
                        "fixture_name": f_name,
                        "total_qty": f_total_qty,
                        "warehouse": f_wh,
                        "total_cost": f_cost,
                        "unit_cost": unit_c,
                    }
                )
                st.success(f"[{f_name}] 집기가 등록되었습니다.")
                st.rerun()
            else:
                st.error("집기명을 입력해 주세요.")

    st.markdown("---")
    st.write("##### 📊 집기 자산 및 잔여 현황 (출고 반영 자동 계산)")

    if st.session_state.master_fixtures:
        logs = st.session_state.get("stock_logs", [])
        fixtures_display = []

        for fix in st.session_state.master_fixtures:
            f_name = fix["fixture_name"]
            total_q = fix["total_qty"]

            # 출고 이력 중 해당 집기 출고량 차감
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

            fixtures_display.append(
                {
                    "집기명": f_name,
                    "입고 창고": fix["warehouse"],
                    "최초 제작수량": f"{total_q:,} 개",
                    "출고 누적수량": f"{out_q:,} 개",
                    "현재 잔여수량": f"{calc_rem_q:,} 개",
                    "총 제작비 (엔)": f"¥{int(fix['total_cost']):,}",
                    "개당 제작단가 (엔)": f"¥{unit_c:,.2f}",
                    "잔여 자산가치 (엔)": f"¥{int(rem_value):,}",
                }
            )

        st.dataframe(pd.DataFrame(fixtures_display), use_container_width=True)
    else:
        st.info("등록된 집기 자산이 없습니다.")
