import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar

st.set_page_config(page_title="마스터상품 관리", layout="wide")
render_sidebar()

# DB 테이블 초기화
db.init_db()

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
# TAB 1: 등록된 상품 마스터 목록 & 삭제 기능
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

        # 삭제용 체크박스 칼럼 추가 (기본값 False)
        df_p["선택"] = False

        # 필요 칼럼 순서 정렬 ("선택" 열을 제일 앞으로 배치)
        target_cols = [
            "선택",
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
        mapping_dict = COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"])
        mapping_dict["선택"] = "선택"  # 선택 체크박스 칼럼 유지
        df_p_renamed = df_p_filtered.rename(columns=mapping_dict)

        # 현재 언어별 매입단가, 소비자가, 입수량 칼럼명 매핑
        cost_col = mapping_dict.get("cost_price_krw", "매입단가(원)")
        list_col = mapping_dict.get("list_price_jpy_excl_tax", "소비자 가(엔, 세외)")
        unit_col = mapping_dict.get("units_per_box", "BOX 입수량(EA)")

        edited_df = st.data_editor(
            df_p_renamed,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", help="삭제할 상품을 체크하세요.", default=False),
                cost_col: st.column_config.NumberColumn(cost_col, format="₩%,d"),
                list_col: st.column_config.NumberColumn(list_col, format="¥%,d"),
                unit_col: st.column_config.NumberColumn(unit_col, format="%,d"),
            },
            key="master_product_editor",
        )

        btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 5])

        # 1. 수정사항 저장 버튼
        with btn_col1:
            if st.button("💾 상품 변경사항 저장", type="primary", use_container_width=True):
                # '선택' 열 제거 후 저장
                save_df = edited_df.drop(columns=["선택"], errors="ignore")

                inv_map = {
                    v: k
                    for k, v in COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"]).items()
                }
                saved_records = save_df.rename(columns=inv_map).to_dict("records")

                # jan_code 키 동기화 (타 화면 참조용)
                for item in saved_records:
                    item["jan_code"] = item.get("box_jan_code", "")

                st.session_state.master_products = saved_records
                st.session_state.products = saved_records  # 전체 시스템 공유용 상품 세션 동기화

                st.success("상품 마스터가 성공적으로 저장되었습니다.")
                st.rerun()

        # 2. 선택 항목 삭제 버튼
        with btn_col2:
            if st.button("🗑️ 선택한 상품 삭제", type="secondary", use_container_width=True):
                selected_rows = edited_df[edited_df["선택"] == True]

                if selected_rows.empty:
                    st.warning("삭제할 상품을 목록에서 먼저 체크해 주세요.")
                else:
                    # 선택 안 된 행들만 남기기
                    remaining_df = edited_df[edited_df["선택"] == False].drop(columns=["선택"], errors="ignore")

                    inv_map = {
                        v: k
                        for k, v in COLUMN_MAPS.get(lang, COLUMN_MAPS["한국어"]).items()
                    }
                    updated_records = remaining_df.rename(columns=inv_map).to_dict("records")

                    for item in updated_records:
                        item["jan_code"] = item.get("box_jan_code", "")

                    st.session_state.master_products = updated_records
                    st.session_state.products = updated_records  # 시스템 동기화

                    st.success(f"{len(selected_rows)}개 상품이 성공적으로 삭제되었습니다.")
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
# TAB 3: 집기 마스터 & 자산 관리 (제작수량 변경 시 잔여수량 자동 계산 및 반영)
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
    st.write("##### 📊 집기 자산 및 잔여 현황 (수정/삭제 기능 연동)")

    if st.session_state.master_fixtures:
        logs = st.session_state.get("stock_logs", [])
        df_f = pd.DataFrame(st.session_state.master_fixtures)

        # 삭제용 체크박스 열 추가
        df_f["선택"] = False

        # 출고 누적량 및 잔여 현황 자동 계산열 추가
        out_qtys = []
        calc_rem_qtys = []
        rem_values = []

        for _, fix in df_f.iterrows():
            f_n = fix.get("fixture_name", "")
            t_q = int(fix.get("total_qty", 0))
            t_c = float(fix.get("total_cost", 0))

            # 재고 로그에서 출고된 누적 수량 계산
            out_q = sum(
                l.get("qty", 0)
                for l in logs
                if l.get("product_name") == f_n
                and l.get("type") == "출고"
                and l.get("item_category") == "집기"
            )
            # 현재 잔여수량 = 제작수량 - 출고 누적수량
            c_rem_q = max(0, t_q - out_q)
            u_c = round(t_c / t_q, 2) if t_q > 0 else 0
            r_val = round(u_c * c_rem_q, 2)

            out_qtys.append(out_q)
            calc_rem_qtys.append(c_rem_q)
            rem_values.append(r_val)

        df_f["out_qty"] = out_qtys
        df_f["calc_rem_qty"] = calc_rem_qtys
        df_f["rem_value"] = rem_values

        # 컬럼 순서 정리 및 매핑
        f_target_cols = [
            "선택",
            "fixture_name",
            "warehouse",
            "total_qty",
            "out_qty",
            "calc_rem_qty",
            "total_cost",
            "unit_cost",
            "rem_value",
        ]
        existing_f_cols = [c for c in f_target_cols if c in df_f.columns]
        df_f_filtered = df_f[existing_f_cols]

        f_mapping_dict = {
            "선택": "선택",
            "fixture_name": "집기명",
            "warehouse": "입고 창고",
            "total_qty": "최초 제작수량",
            "out_qty": "출고 누적수량",
            "calc_rem_qty": "현재 잔여수량",
            "total_cost": "총 제작비 (엔)",
            "unit_cost": "개당 제작단가 (엔)",
            "rem_value": "잔여 자산가치 (엔)",
        }

        df_f_renamed = df_f_filtered.rename(columns=f_mapping_dict)

        edited_f_df = st.data_editor(
            df_f_renamed,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", help="삭제할 집기를 체크하세요.", default=False),
                "최초 제작수량": st.column_config.NumberColumn("최초 제작수량", format="%,d"),
                "출고 누적수량": st.column_config.NumberColumn("출고 누적수량", format="%,d", disabled=True),
                "현재 잔여수량": st.column_config.NumberColumn("현재 잔여수량", format="%,d", disabled=True),
                "총 제작비 (엔)": st.column_config.NumberColumn("총 제작비 (엔)", format="¥%,d"),
                "개당 제작단가 (엔)": st.column_config.NumberColumn("개당 제작단가 (엔)", format="¥%,.2f", disabled=True),
                "잔여 자산가치 (엔)": st.column_config.NumberColumn("잔여 자산가치 (엔)", format="¥%,d", disabled=True),
            },
            key="master_fixture_editor",
        )

        f_btn_col1, f_btn_col2, _ = st.columns([1.5, 1.5, 5])

        # 1. 집기 수정사항 저장 (제작수량 수정 시 잔여수량 재계산)
        with f_btn_col1:
            if st.button("💾 집기 변경사항 저장", type="primary", use_container_width=True):
                save_f_df = edited_f_df.drop(columns=["선택"], errors="ignore")

                inv_f_map = {v: k for k, v in f_mapping_dict.items() if k != "선택"}
                saved_f_records = save_f_df.rename(columns=inv_f_map).to_dict("records")

                clean_fixtures = []
                for fix in saved_f_records:
                    f_n = str(fix.get("fixture_name", ""))
                    tot_q = int(fix.get("total_qty", 0))
                    tot_c = float(fix.get("total_cost", 0))
                    
                    # 제작수량이 변경되더라도 출고 누적수량과 연동하여 잔여수량 및 자산가치 자동 재계산
                    u_cost = round(tot_c / tot_q, 2) if tot_q > 0 else 0

                    clean_fixtures.append({
                        "fixture_name": f_n,
                        "total_qty": tot_q,
                        "warehouse": str(fix.get("warehouse", "")),
                        "total_cost": tot_c,
                        "unit_cost": u_cost,
                    })

                st.session_state.master_fixtures = clean_fixtures
                st.success("집기 마스터가 성공적으로 저장되었으며, 잔여수량 및 가치가 자동 재계산되었습니다.")
                st.rerun()

        # 2. 선택한 집기 삭제
        with f_btn_col2:
            if st.button("🗑️ 선택한 집기 삭제", type="secondary", use_container_width=True):
                selected_f_rows = edited_f_df[edited_f_df["선택"] == True]

                if selected_f_rows.empty:
                    st.warning("삭제할 집기를 목록에서 먼저 체크해 주세요.")
                else:
                    remaining_f_df = edited_f_df[edited_f_df["선택"] == False].drop(columns=["선택"], errors="ignore")

                    inv_f_map = {v: k for k, v in f_mapping_dict.items() if k != "선택"}
                    updated_f_records = remaining_f_df.rename(columns=inv_f_map).to_dict("records")

                    clean_fixtures = []
                    for fix in updated_f_records:
                        tot_q = int(fix.get("total_qty", 0))
                        tot_c = float(fix.get("total_cost", 0))
                        u_cost = round(tot_c / tot_q, 2) if tot_q > 0 else 0

                        clean_fixtures.append({
                            "fixture_name": str(fix.get("fixture_name", "")),
                            "total_qty": tot_q,
                            "warehouse": str(fix.get("warehouse", "")),
                            "total_cost": tot_c,
                            "unit_cost": u_cost,
                        })

                    st.session_state.master_fixtures = clean_fixtures
                    st.success(f"{len(selected_f_rows)}개 집기가 성공적으로 삭제되었습니다.")
                    st.rerun()
    else:
        st.info("등록된 집기 자산이 없습니다.")
