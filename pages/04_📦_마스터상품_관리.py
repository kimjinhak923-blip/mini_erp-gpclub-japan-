import pandas as pd
import streamlit as st

st.set_page_config(page_title="마스터상품 관리", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

user = st.session_state.logged_in_user
is_admin = user.get("role") == "관리자" or user["id"] == "admin"
is_visitor = user.get("role") == "방문자"

st.header("📦 마스터 상품 등록 및 관리 (가로 배치 레이아웃)")

with st.expander("➕ 신규 마스터 상품 등록", expanded=True):
    with st.form("new_master_product_form"):
        r1_1, r1_2, r1_3, r1_4 = st.columns(4)
        p_code = r1_1.text_input("상품코드 * (예: PRD-1002)")
        p_name = r1_2.text_input("제품명 *")
        p_category = r1_3.text_input("카테고리 *", value="화장품/뷰티")
        p_price = r1_4.number_input("매입단가(엔) *", min_value=0, step=100)

        r2_1, r2_2, r2_3, r2_4 = st.columns(4)
        p_jan_pack = r2_1.text_input("JAN(곽)")
        p_jan_single = r2_2.text_input("JAN(낱장)")
        p_capacity = r2_3.text_input("용량")
        p_in_pack_qty = r2_4.text_input("입수량(곽/낱장)")

        r3_1, r3_2, r3_3, r3_4 = st.columns(4)
        p_prod_size = r3_1.text_input("제품사이즈(곽)")
        p_box_size = r3_2.text_input("박스사이즈(가*세*높)")
        p_plt_qty = r3_3.text_input("1 PLT 수량")
        p_vendor = r3_4.text_input("공급업체/제조사")

        if st.form_submit_button("마스터 상품 등록", disabled=is_visitor):
            if not p_code or not p_name:
                st.error("상품코드와 제품명은 필수입니다.")
            elif any(p["code"] == p_code for p in st.session_state.master_products):
                st.error("이미 등록된 상품코드입니다.")
            else:
                st.session_state.master_products.append({
                    "code": p_code,
                    "name": p_name,
                    "jan_pack": p_jan_pack,
                    "jan_single": p_jan_single,
                    "capacity": p_capacity,
                    "category": p_category,
                    "price": p_price,
                    "in_pack_qty": p_in_pack_qty,
                    "prod_size": p_prod_size,
                    "box_size": p_box_size,
                    "plt_qty": p_plt_qty,
                    "vendor": p_vendor,
                })
                st.success("등록 완료!")
                st.rerun()

st.markdown("---")
st.subheader("📋 마스터 상품 목록 및 가로 즉시 수정")

if st.session_state.master_products:
    st.dataframe(pd.DataFrame(st.session_state.master_products), use_container_width=True)

    st.subheader("🛠️ 선택 상품 정보 저장 / 삭제")
    p_codes = [p["code"] for p in st.session_state.master_products]
    target_code = st.selectbox("수정할 상품 선택", p_codes)
    target_p = next(p for p in st.session_state.master_products if p["code"] == target_code)

    with st.form("edit_master_product_horizontal"):
        e1, e2, e3, e4, e5 = st.columns(5)
        e_name = e1.text_input("제품명", value=target_p["name"])
        e_cat = e2.text_input("카테고리", value=target_p["category"])
        e_price = e3.number_input("매입단가", min_value=0, value=int(target_p["price"]))
        e_jan_p = e4.text_input("JAN(곽)", value=target_p.get("jan_pack", ""))
        e_jan_s = e5.text_input("JAN(낱장)", value=target_p.get("jan_single", ""))

        btn_col1, btn_col2 = st.columns([1, 1])
        if btn_col1.form_submit_button("💾 수정사항 저장", disabled=is_visitor):
            target_p["name"] = e_name
            target_p["category"] = e_cat
            target_p["price"] = e_price
            target_p["jan_pack"] = e_jan_p
            target_p["jan_single"] = e_jan_s
            st.success("수정 저장이 완료되었습니다.")
            st.rerun()

        if btn_col2.form_submit_button("❌ 선택 상품 삭제", disabled=not is_admin):
            st.session_state.master_products.remove(target_p)
            st.success("삭제되었습니다.")
            st.rerun()
