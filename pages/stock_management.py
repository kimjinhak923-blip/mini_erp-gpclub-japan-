import datetime
import pandas as pd
import streamlit as st
import db  # 데이터베이스 모듈 불러오기
from sidebar_menu import render_sidebar

st.set_page_config(page_title="입출고 및 재고 관리", layout="wide")
render_sidebar()

# DB 테이블 초기화
db.init_db()

st.title("🚚 입출고 등록 및 재고 관리")
st.markdown("---")

# DB 최신 데이터 동기화
clients = db.load_clients()
products = db.load_products()
fixtures = db.load_fixtures()
warehouses = [w["warehouse_name"] for w in db.load_warehouses()]

client_names = [c["client_name"] for c in clients] if clients else ["일반"]
product_names = [p["product_name"] for p in products] if products else []
fixture_names = [f["fixture_name"] for f in fixtures] if fixtures else []

tab1, tab2, tab3 = st.tabs(
    ["📥 입출고 등록", "📊 실시간 재고 현황", "📜 입출고 전체 내역"]
)

# -----------------------------------------------------------------------------
# TAB 1: 입출고 신규 등록
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("신규 입출고 내역 입력")

    with st.form("add_stock_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            log_date = st.date_input("일자", datetime.date.today())
            log_type = st.selectbox("구분", ["입고", "출고"])
            item_category = st.selectbox("구분 카테고리", ["상품", "집기"])

        with col2:
            if item_category == "상품":
                item_name = st.selectbox(
                    "상품 선택",
                    product_names
                    if product_names
                    else ["등록된 상품 없음"],
                )
            else:
                item_name = st.selectbox(
                    "집기 선택",
                    fixture_names
                    if fixture_names
                    else ["등록된 집기 없음"],
                )

            client_selected = st.selectbox("거래처 선택", client_names)

        with col3:
            wh_selected = st.selectbox("창고 선택", warehouses)
            qty = st.number_input("수량(EA)", min_value=1, value=1)
            note = st.text_input("비고", placeholder="예: POP 매장 전달 건")

        if st.form_submit_button("입출고 내역 저장", type="primary"):
            if (
                item_category == "상품" and item_name == "등록된 상품 없음"
            ) or (item_category == "집기" and item_name == "등록된 집기 없음"):
                st.error("먼저 마스터 관리에서 상품 또는 집기를 등록해 주세요.")
            else:
                db.add_stock_log(
                    date=str(log_date),
                    log_type=log_type,
                    item_category=item_category,
                    product_name=item_name,
                    warehouse=wh_selected,
                    qty=qty,
                    client_name=client_selected,
                    note=note,
                )
                st.success("입출고 내역이 DB에 영구 저장되었습니다.")
                st.rerun()

# -----------------------------------------------------------------------------
# TAB 2: 실시간 재고 현황
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("창고별 / 품목별 현재 재고 현황")
    stock_data = db.get_current_stock()

    if stock_data:
        df_stock = pd.DataFrame(stock_data)
        df_stock.rename(
            columns={
                "warehouse": "창고명",
                "product_name": "품목명",
                "item_category": "카테고리",
                "current_stock": "현재 재고수량",
            },
            inplace=True,
        )

        st.dataframe(df_stock, use_container_width=True)
    else:
        st.info("등록된 입출고 내역이 없어 재고 데이터가 없습니다.")

# -----------------------------------------------------------------------------
# TAB 3: 입출고 전체 내역 및 수정/삭제
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("전체 입출고 내역")
    logs = db.load_stock_logs()

    if logs:
        df_logs = pd.DataFrame(logs)
        df_logs["선택"] = False

        edited_logs = st.data_editor(
            df_logs,
            use_container_width=True,
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", default=False),
                "id": st.column_config.NumberColumn("ID", disabled=True),
            },
            key="stock_logs_editor",
        )

        b_col1, b_col2, _ = st.columns([1.5, 1.5, 5])
        with b_col1:
            if st.button("💾 변경사항 저장", type="primary"):
                updated_logs = edited_logs.drop(
                    columns=["선택"], errors="ignore"
                ).to_dict("records")
                db.save_stock_logs_bulk(updated_logs)
                st.success("입출고 내역 변경사항이 DB에 저장되었습니다.")
                st.rerun()

        with b_col2:
            if st.button("🗑️ 선택 삭제", type="secondary"):
                remaining_logs = edited_logs[edited_logs["선택"] == False].drop(
                    columns=["선택"], errors="ignore"
                )
                db.save_stock_logs_bulk(remaining_logs.to_dict("records"))
                st.success("선택한 내역이 삭제되었습니다.")
                st.rerun()
    else:
        st.info("입출고 내역이 없습니다.")
