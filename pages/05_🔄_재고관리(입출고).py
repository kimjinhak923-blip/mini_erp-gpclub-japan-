import datetime
import io
import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# 1. 다국어 딕셔너리 정의 (한국어 / 일본어 / 영어)
TRANSLATIONS = {
    "KO": {
        "page_title": "재고관리(입출고)",
        "title": "📦 재고 입출고 및 출고 등록",
        "tab1": "📤 일반 출고 등록 (제품/집기 선택)",
        "tab2": "📥 개별 입고 등록",
        "tab3": "📁 엑셀 대량 업로드",
        # Tab 1
        "sub_out_title": "📋 출고 지시 및 발주 등록",
        "out_wh": "출고 창고",
        "order_no": "발주번호",
        "order_code": "발주관리번호",
        "sel_client": "거래처 선택",
        "no_client": "등록된 거래처 없음",
        "order_date": "발주일",
        "delivery_date": "납품 희망일",
        "dest_name": "납품처명",
        "dest_zip": "우편번호",
        "dest_addr": "납품처 주소",
        "dest_tel": "납품처 전화번호",
        "out_list_title": "##### 📦 출고 등록 품목 목록",
        "item_no": "품목",
        "cat_label": "구분",
        "cat_prod": "제품",
        "cat_fix": "집기",
        "select_prod": "상품 선택",
        "no_prod": "등록된 상품 없음",
        "select_fix": "집기 선택",
        "no_fix": "등록된 집기 없음",
        "box_jan": "곽 JAN",
        "single_jan": "낱장 JAN",
        "fix_no_charge": "🎪 집기 품목 (무상 출고)",
        "qty_label": "수량",
        "box_qty_label": "Box 수량",
        "purpose_label": "용도",
        "purp_deliver": "납품",
        "purp_foc": "FOC",
        "purp_sample": "샘플",
        "purp_fixture": "집기출고",
        "price_label": "공급단가",
        "amount_label": "금액",
        "price_free_fix": "무상(집기)",
        "btn_add_item": "➕ 품목 추가",
        "btn_del_item": "➖ 품목 삭제",
        "m_item_cnt": "등록 품목 수",
        "m_total_qty": "총 출고 수량",
        "m_total_box": "총 출고 Box 수량",
        "m_total_amt": "총 발주 금액 (무상 제외)",
        "btn_submit_out": "🚀 출고 확정 및 저장",
        "msg_out_success": "출고 등록 완료 및 집기/제품 이력이 정상 등록되었습니다!",
        # Tab 2
        "sub_in_title": "📥 개별 입고 등록",
        "in_wh": "입고 창고",
        "in_prod_sel": "상품 선택 (마스터 등록 상품)",
        "no_in_prod": "상품 없음",
        "in_qty": "입고 수량",
        "in_price": "매입 단가 (원/엔)",
        "purp_buy": "매입",
        "info_total_buy": "💡 총 매입 금액:",
        "foc_free_in": "FOC 무상 입고",
        "auto_calc": "자동 연산",
        "btn_submit_in": "📥 입고 등록 실행",
        "msg_in_success": "입고 처리가 완료되었습니다.",
        # Tab 3
        "sub_excel_title": "📁 1~2년치 입출고 데이터 엑셀 대량 업로드",
        "btn_dl_template": "📥 엑셀 업로드 양식 다운로드 (.xlsx)",
        "sub_excel_up": "📤 작성된 엑셀 파일 업로드 및 데이터 반영",
        "file_uploader_label": "작성된 입출고 엑셀 파일을 선택하세요",
        "msg_excel_read": "파일을 성공적으로 읽어왔습니다!",
        "preview_title": "##### 🔍 업로드 데이터 미리보기",
        "btn_submit_excel": "🚀 대량 업로드 실행 및 이력 저장",
        "msg_excel_success": "총 {}건의 입출고 데이터 업로드가 완료되었습니다! '입출고 이력조회' 페이지에서 확인하실 수 있습니다.",
        "msg_excel_err": "엑셀 파일 읽기 및 처리 중 오류가 발생했습니다:",
        # Worker & Status
        "worker_admin": "관리자",
        "worker_excel": "관리자(엑셀업로드)",
        "status_out_done": "출고완료",
        "status_in_done": "입고완료",
        "unit_pcs": "개",
    },
    "JA": {
        "page_title": "在庫管理(入出荷)",
        "title": "📦 在庫入出荷および出荷登録",
        "tab1": "📤 一般出荷登録 (商品/什器選択)",
        "tab2": "📥 個別入庫登録",
        "tab3": "📁 エクセル一括アップロード",
        "sub_out_title": "📋 出荷指示および発注登録",
        "out_wh": "出荷倉庫",
        "order_no": "発注番号",
        "order_code": "発注管理番号",
        "sel_client": "取引先選択",
        "no_client": "登録された取引先なし",
        "order_date": "発注日",
        "delivery_date": "納品希望日",
        "dest_name": "納品先名",
        "dest_zip": "郵便番号",
        "dest_addr": "納品先住所",
        "dest_tel": "納品先電話番号",
        "out_list_title": "##### 📦 出荷登録品目リスト",
        "item_no": "品目",
        "cat_label": "区分",
        "cat_prod": "製品",
        "cat_fix": "什器",
        "select_prod": "商品選択",
        "no_prod": "登録された商品なし",
        "select_fix": "什器選択",
        "no_fix": "登録された什器なし",
        "box_jan": "箱JAN",
        "single_jan": "単品JAN",
        "fix_no_charge": "🎪 什器品目 (無償出荷)",
        "qty_label": "数量",
        "box_qty_label": "Box数量",
        "purpose_label": "用途",
        "purp_deliver": "納品",
        "purp_foc": "FOC",
        "purp_sample": "サンプル",
        "purp_fixture": "什器出荷",
        "price_label": "供給単価",
        "amount_label": "金額",
        "price_free_fix": "無償(什器)",
        "btn_add_item": "➕ 品目追加",
        "btn_del_item": "➖ 品目削除",
        "m_item_cnt": "登録品目数",
        "m_total_qty": "総出荷数量",
        "m_total_box": "総出荷Box数量",
        "m_total_amt": "総発注金額 (無償除く)",
        "btn_submit_out": "🚀 出荷確定および保存",
        "msg_out_success": "出荷登録が完了し、什器/製品の履歴が正常に登録されました！",
        "sub_in_title": "📥 個別入庫登録",
        "in_wh": "入庫倉庫",
        "in_prod_sel": "商品選択 (マスター登録商品)",
        "no_in_prod": "商品なし",
        "in_qty": "入庫数量",
        "in_price": "仕入単価 (円)",
        "purp_buy": "仕入",
        "info_total_buy": "💡 総仕入金額:",
        "foc_free_in": "FOC 無償入庫",
        "auto_calc": "自動計算",
        "btn_submit_in": "📥 入庫登録実行",
        "msg_in_success": "入庫処理が完了しました。",
        "sub_excel_title": "📁 1〜2年分入出荷データのエクセル一括アップロード",
        "btn_dl_template": "📥 エクセルアップロードフォーマットダウンロード (.xlsx)",
        "sub_excel_up": "📤 作成済みエクセルファイルのアップロードおよび反映",
        "file_uploader_label": "作成した入出荷エクセルファイルを選択してください",
        "msg_excel_read": "ファイルを正常に読み込みました！",
        "preview_title": "##### 🔍 アップロードデータのプレビュー",
        "btn_submit_excel": "🚀 一括アップロード実行および履歴保存",
        "msg_excel_success": "合計{}件の入出荷データのアップロードが完了しました！「入出荷履歴照会」ページでご確認いただけます。",
        "msg_excel_err": "エクセルファイルの読み込みおよび処理中にエラーが発生しました:",
        "worker_admin": "管理者",
        "worker_excel": "管理者(エクセルアップロード)",
        "status_out_done": "出荷完了",
        "status_in_done": "入庫完了",
        "unit_pcs": "個",
    },
    "EN": {
        "page_title": "Stock Management (In/Out)",
        "title": "📦 Stock In/Out & Outbound Registration",
        "tab1": "📤 Outbound Registration (Product/Fixture)",
        "tab2": "📥 Individual Inbound Registration",
        "tab3": "📁 Bulk Excel Upload",
        "sub_out_title": "📋 Outbound Instruction & Order Registration",
        "out_wh": "Outbound Warehouse",
        "order_no": "PO Number",
        "order_code": "Order Mgmt Code",
        "sel_client": "Select Client",
        "no_client": "No registered clients",
        "order_date": "Order Date",
        "delivery_date": "Desired Delivery Date",
        "dest_name": "Delivery Destination Name",
        "dest_zip": "Postal Code",
        "dest_addr": "Destination Address",
        "dest_tel": "Destination Phone",
        "out_list_title": "##### 📦 Registered Items List",
        "item_no": "Item",
        "cat_label": "Category",
        "cat_prod": "Product",
        "cat_fix": "Fixture",
        "select_prod": "Select Product",
        "no_prod": "No registered products",
        "select_fix": "Select Fixture",
        "no_fix": "No registered fixtures",
        "box_jan": "Box JAN",
        "single_jan": "Single JAN",
        "fix_no_charge": "🎪 Fixture Item (Free Delivery)",
        "qty_label": "Quantity",
        "box_qty_label": "Box Qty",
        "purpose_label": "Purpose",
        "purp_deliver": "Delivery",
        "purp_foc": "FOC",
        "purp_sample": "Sample",
        "purp_fixture": "Fixture Outbound",
        "price_label": "Unit Price",
        "amount_label": "Total Amount",
        "price_free_fix": "Free (Fixture)",
        "btn_add_item": "➕ Add Item",
        "btn_del_item": "➖ Delete Item",
        "m_item_cnt": "Registered Items",
        "m_total_qty": "Total Outbound Qty",
        "m_total_box": "Total Outbound Boxes",
        "m_total_amt": "Total Order Amount (Excl. Free)",
        "btn_submit_out": "🚀 Confirm & Save Outbound",
        "msg_out_success": "Outbound registration and history updated successfully!",
        "sub_in_title": "📥 Individual Inbound Registration",
        "in_wh": "Inbound Warehouse",
        "in_prod_sel": "Select Product (Master List)",
        "no_in_prod": "No products available",
        "in_qty": "Inbound Qty",
        "in_price": "Purchase Unit Price (JPY)",
        "purp_buy": "Purchase",
        "info_total_buy": "💡 Total Purchase Amount:",
        "foc_free_in": "FOC Free Inbound",
        "auto_calc": "Auto-calculated",
        "btn_submit_in": "📥 Execute Inbound Registration",
        "msg_in_success": "Inbound registration completed successfully.",
        "sub_excel_title": "📁 Bulk Excel Upload (1-2 Years Stock Logs)",
        "btn_dl_template": "📥 Download Excel Template (.xlsx)",
        "sub_excel_up": "📤 Upload Excel File & Apply Data",
        "file_uploader_label": "Select prepared stock log Excel file",
        "msg_excel_read": "File read successfully!",
        "preview_title": "##### 🔍 Uploaded Data Preview",
        "btn_submit_excel": "🚀 Execute Bulk Upload & Save History",
        "msg_excel_success": "Total {} records uploaded successfully! Check 'Inbound/Outbound History' page.",
        "msg_excel_err": "An error occurred while reading or processing the Excel file:",
        "worker_admin": "Admin",
        "worker_excel": "Admin (Excel Upload)",
        "status_out_done": "Outbound Completed",
        "status_in_done": "Inbound Completed",
        "unit_pcs": "pcs",
    },
}

# 2. 현재 선택된 언어 감지 ('lang' 또는 'language' 세션 키 참조)
current_lang = st.session_state.get("lang") or st.session_state.get("language") or "KO"
if current_lang not in TRANSLATIONS:
    current_lang = "KO"

t = TRANSLATIONS[current_lang]

# 3. Streamlit 페이지 설정 (최상단 고정)
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 및 사용자 권한
render_sidebar()
user = st.session_state.get("logged_in_user")

# 5. 메인 타이틀 및 탭 설정
st.title(t["title"])
st.markdown("---")

tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

# --- [TAB 1] 출고 등록 ---
with tab1:
    st.subheader(t["sub_out_title"])

    if "out_items_count" not in st.session_state:
        st.session_state.out_items_count = 1

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        out_wh = st.selectbox(t["out_wh"], ["SAGAWA", "L&K", "大吉商事"])
        order_no = st.text_input(t["order_no"], value="PO-20260813-001")
        order_code = st.text_input(t["order_code"], value="20260813-01")
    with col_h2:
        cli_names = [c["client_name"] for c in st.session_state.get("clients", [])]
        sel_client = st.selectbox(
            t["sel_client"], cli_names if cli_names else [t["no_client"]]
        )
        order_date = st.date_input(t["order_date"], datetime.date.today())
        delivery_date = st.date_input(t["delivery_date"], datetime.date.today())
    with col_h3:
        dest_name = st.text_input(t["dest_name"], value="도쿄 물류 센터")
        dest_zip = st.text_input(t["dest_zip"], value="100-0001")
        dest_addr = st.text_input(t["dest_addr"], value="東京都千代田区1-1")
        dest_tel = st.text_input(t["dest_tel"], value="03-1234-5678")

    st.markdown("---")
    st.write(t["out_list_title"])

    master_prods = st.session_state.get("master_products", [])
    master_fixs = st.session_state.get("master_fixtures", [])

    prod_options = [
        f"{p['product_name']} (곽:{p.get('box_jan_code', p.get('jan_code',''))})"
        for p in master_prods
    ]
    fix_options = [
        f"{f['fixture_name']} (창고:{f['warehouse']})" for f in master_fixs
    ]

    items_data = []

    # 구분 및 용도 선택용 다국어-내부코드 매핑 (계산 안정성 보장)
    cat_options = [t["cat_prod"], t["cat_fix"]]
    cat_map_display_to_code = {t["cat_prod"]: "제품", t["cat_fix"]: "집기"}

    purp_options_prod = [t["purp_deliver"], t["purp_foc"], t["purp_sample"]]
    purp_map_display_to_code = {
        t["purp_deliver"]: "납품",
        t["purp_foc"]: "FOC",
        t["purp_sample"]: "샘플",
        t["purp_fixture"]: "집기출고",
    }

    for i in range(st.session_state.out_items_count):
        st.markdown(f"**{t['item_no']} #{i+1}**")
        c_cat, c_p, c_qty, c_box, c_price, c_amt, c_purp = st.columns(
            [1.2, 2.5, 1, 1, 1.2, 1.2, 1]
        )

        with c_cat:
            sel_cat_disp = st.selectbox(t["cat_label"], cat_options, key=f"cat_{i}")
            # 계산용 내부 코드 연동
            item_cat = cat_map_display_to_code.get(sel_cat_disp, "제품")

        with c_p:
            if item_cat == "제품":
                selected_str = st.selectbox(
                    f"{t['select_prod']} #{i+1}",
                    prod_options if prod_options else [t["no_prod"]],
                    key=f"p_select_{i}",
                )
                p_name = (
                    selected_str.split(" (")[0]
                    if " (" in selected_str
                    else selected_str
                )
                matched_p = next(
                    (p for p in master_prods if p["product_name"] == p_name),
                    None,
                )
                jan_disp = (
                    matched_p.get(
                        "box_jan_code", matched_p.get("jan_code", "")
                    )
                    if matched_p
                    else ""
                )
                single_jan = (
                    matched_p.get("single_jan_code", "-") if matched_p else "-"
                )
                st.caption(
                    f"{t['box_jan']}: `{jan_disp}` | {t['single_jan']}: `{single_jan}`"
                )
            else:
                selected_str = st.selectbox(
                    f"{t['select_fix']} #{i+1}",
                    fix_options if fix_options else [t["no_fix"]],
                    key=f"f_select_{i}",
                )
                p_name = (
                    selected_str.split(" (")[0]
                    if " (" in selected_str
                    else selected_str
                )
                matched_p = next(
                    (f for f in master_fixs if f["fixture_name"] == p_name),
                    None,
                )
                jan_disp = "-"
                st.caption(t["fix_no_charge"])

        with c_qty:
            qty = st.number_input(
                f"{t['qty_label']} #{i+1}", min_value=1, value=10, key=f"qty_{i}"
            )

        with c_box:
            if item_cat == "제품" and matched_p:
                units_per_box = matched_p.get("units_per_box", 1)
                box_count = round(qty / units_per_box, 2)
                box_disp = f"{box_count} Box"
            else:
                box_count = 0
                box_disp = "-"
            st.text_input(
                f"{t['box_qty_label']} #{i+1}",
                value=box_disp,
                disabled=True,
                key=f"box_{i}",
            )

        with c_purp:
            if item_cat == "제품":
                sel_purp_disp = st.selectbox(
                    f"{t['purpose_label']} #{i+1}",
                    purp_options_prod,
                    key=f"purp_{i}",
                )
                purpose = purp_map_display_to_code.get(sel_purp_disp, "납품")
            else:
                purpose = "집기출고"
                st.text_input(
                    f"{t['purpose_label']} #{i+1}",
                    value=t["purp_fixture"],
                    disabled=True,
                    key=f"purp_dis_{i}",
                )

        with c_price:
            if item_cat == "제품" and purpose == "납품":
                custom_p = next(
                    (
                        cp
                        for cp in st.session_state.get("client_products", [])
                        if cp["client_name"] == sel_client
                        and cp.get("product_name") == p_name
                    ),
                    None,
                )
                unit_price = (
                    custom_p["custom_supply_price"]
                    if custom_p
                    else (
                        matched_p["supply_price_jpy"] if matched_p else 0
                    )
                )
                price_disp = f"¥{unit_price:,.0f}"
                calc_amt = unit_price * qty
            elif item_cat == "제품":
                unit_price = 0
                price_disp = sel_purp_disp
                calc_amt = 0
            else:
                unit_price = 0
                price_disp = t["price_free_fix"]
                calc_amt = 0

            st.text_input(
                f"{t['price_label']} #{i+1}",
                value=price_disp,
                disabled=True,
                key=f"price_{i}",
            )

        with c_amt:
            amt_disp = (
                f"¥{calc_amt:,.0f}"
                if (item_cat == "제품" and purpose == "납품")
                else price_disp
            )
            st.text_input(
                f"{t['amount_label']} #{i+1}", value=amt_disp, disabled=True, key=f"amt_{i}"
            )

        items_data.append({
            "item_category": item_cat,
            "p_name": p_name,
            "jan": jan_disp,
            "qty": qty,
            "box_qty": box_count,
            "unit_price": unit_price,
            "total_amount": calc_amt,
            "purpose": purpose,
        })

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.session_state.out_items_count < 30:
            if st.button(t["btn_add_item"], use_container_width=True):
                st.session_state.out_items_count += 1
                st.rerun()
    with col_btn2:
        if st.session_state.out_items_count > 1:
            if st.button(t["btn_del_item"]):
                st.session_state.out_items_count -= 1
                st.rerun()

    st.markdown("---")

    total_prod_count = len(items_data)
    total_out_qty = sum(item["qty"] for item in items_data)
    total_out_box = sum(item["box_qty"] for item in items_data)
    total_order_amount = sum(item["total_amount"] for item in items_data)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t["m_item_cnt"], f"{total_prod_count:,} {t['unit_pcs']}")
    m2.metric(t["m_total_qty"], f"{total_out_qty:,} {t['unit_pcs']}")
    m3.metric(t["m_total_box"], f"{total_out_box:,.2f} Box")
    m4.metric(t["m_total_amt"], f"¥{total_order_amount:,.0f}")

    if st.button(
        t["btn_submit_out"], type="primary", use_container_width=True
    ):
        if "stock_logs" not in st.session_state:
            st.session_state.stock_logs = []
        if "warehouse_stocks" not in st.session_state:
            st.session_state.warehouse_stocks = []

        for item in items_data:
            st.session_state.stock_logs.append({
                "date": str(order_date),
                "delivery_date": str(delivery_date),
                "type": "출고",
                "item_category": item["item_category"],
                "purpose": item["purpose"],
                "jan_code": item["jan"],
                "product_name": item["p_name"],
                "qty": item["qty"],
                "box_qty": item["box_qty"],
                "unit_price": item["unit_price"],
                "total_amount": item["total_amount"],
                "warehouse": out_wh,
                "order_no": order_no,
                "order_code": order_code,
                "status": "출고완료",
                "client_name": sel_client,
                "destination": f"[{dest_name}] {dest_addr} (Tel: {dest_tel})",
                "worker": user["name"] if user else t["worker_admin"],
            })

            # 제품인 경우 재고 차감 (내부 식별자 '제품' 기준)
            if item["item_category"] == "제품":
                stk = next(
                    (
                        s
                        for s in st.session_state.warehouse_stocks
                        if s["warehouse"] == out_wh
                        and s["jan_code"] == item["jan"]
                    ),
                    None,
                )
                if stk:
                    stk["stock_qty"] -= item["qty"]

        st.success(t["msg_out_success"])
        st.session_state.out_items_count = 1
        st.rerun()

# --- [TAB 2] 개별 입고 등록 ---
with tab2:
    st.subheader(t["sub_in_title"])
    in_wh = st.selectbox(
        t["in_wh"], ["SAGAWA", "L&K", "大吉商事"], key="in_wh_sel"
    )
    m_prods = st.session_state.get("master_products", [])
    m_opts = [
        f"{p['product_name']} ({p.get('box_jan_code', p.get('jan_code',''))})"
        for p in m_prods
    ]
    sel_in_prod = st.selectbox(
        t["in_prod_sel"], m_opts if m_opts else [t["no_in_prod"]]
    )

    p_name_in = (
        sel_in_prod.split(" (")[0] if " (" in sel_in_prod else sel_in_prod
    )
    matched_in_p = next(
        (p for p in m_prods if p["product_name"] == p_name_in), None
    )

    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        in_qty = st.number_input(t["in_qty"], min_value=1, value=100)
    with col_i2:
        default_cost = (
            matched_in_p.get("supply_price_jpy", 0) if matched_in_p else 0
        )
        in_unit_cost = st.number_input(
            t["in_price"], min_value=0, value=default_cost
        )
    with col_i3:
        purp_in_disp = st.selectbox(t["purpose_label"], [t["purp_buy"], t["purp_foc"]])
        # 연산용 내부 코드 변환
        in_purpose = "FOC" if purp_in_disp == t["purp_foc"] else "매입"

    total_in_cost = in_qty * in_unit_cost if in_purpose == "매입" else 0
    st.info(
        f"{t['info_total_buy']} **¥{total_in_cost:,.0f}** ({t['foc_free_in'] if in_purpose == 'FOC' else t['auto_calc']})"
    )

    if st.button(t["btn_submit_in"], type="primary"):
        if "stock_logs" not in st.session_state:
            st.session_state.stock_logs = []
        if "warehouse_stocks" not in st.session_state:
            st.session_state.warehouse_stocks = []

        jan_in = (
            matched_in_p.get("box_jan_code", matched_in_p.get("jan_code", ""))
            if matched_in_p
            else ""
        )
        st.session_state.stock_logs.append({
            "date": str(datetime.date.today()),
            "delivery_date": str(datetime.date.today()),
            "type": "입고",
            "item_category": "제품",
            "purpose": in_purpose,
            "jan_code": jan_in,
            "product_name": p_name_in,
            "qty": in_qty,
            "box_qty": round(
                in_qty
                / (matched_in_p["units_per_box"] if matched_in_p else 1),
                2,
            ),
            "unit_price": in_unit_cost,
            "total_amount": total_in_cost,
            "warehouse": in_wh,
            "order_no": "IN-MANUAL",
            "order_code": "-",
            "status": "입고완료",
            "client_name": "-",
            "destination": in_wh,
            "worker": user["name"] if user else t["worker_admin"],
        })

        stk = next(
            (
                s
                for s in st.session_state.warehouse_stocks
                if s["warehouse"] == in_wh and s["jan_code"] == jan_in
            ),
            None,
        )
        if stk:
            stk["stock_qty"] += in_qty
        else:
            st.session_state.warehouse_stocks.append({
                "warehouse": in_wh,
                "jan_code": jan_in,
                "product_name": p_name_in,
                "stock_qty": in_qty,
            })

        st.success(t["msg_in_success"])
        st.rerun()

# --- [TAB 3] 엑셀 대량 업로드 ---
with tab3:
    st.subheader(t["sub_excel_title"])

    # 엑셀 다운로드 양식
    template_df = pd.DataFrame([{
        "발주일": str(datetime.date.today()),
        "납품희망일": str(datetime.date.today()),
        "구분(입고/출고)": "출고",
        "용도(납품/매입/샘플/FOC/집기출고)": "납품",
        "상품명": "프리미엄 수분 크림 50ml",
        "수량": 100,
        "거래처명": "(주)파트너스 코리아",
        "납품처명": "도쿄 물류센터 3번 랙",
        "창고명": "SAGAWA",
        "발주번호": "PO-2026-001",
        "발주관리코드": "ORD-001",
        "상태": "출고완료",
    }])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        template_df.to_excel(writer, index=False, sheet_name="입출고대량등록양식")

    st.download_button(
        label=t["btn_dl_template"],
        data=buffer.getvalue(),
        file_name="ERP_Stock_Import_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown("---")
    st.subheader(t["sub_excel_up"])

    uploaded_file = st.file_uploader(
        t["file_uploader_label"], type=["xlsx", "xls"]
    )

    if uploaded_file is not None:
        try:
            df_upload = pd.read_excel(uploaded_file)
            st.success(t["msg_excel_read"])
            st.write(t["preview_title"])
            st.dataframe(df_upload, use_container_width=True)

            if st.button(
                t["btn_submit_excel"],
                type="primary",
                use_container_width=True,
            ):
                if "stock_logs" not in st.session_state:
                    st.session_state.stock_logs = []
                if "warehouse_stocks" not in st.session_state:
                    st.session_state.warehouse_stocks = []

                master_prods = st.session_state.get("master_products", [])
                master_fixs = st.session_state.get("master_fixtures", [])
                client_prods = st.session_state.get("client_products", [])

                success_count = 0

                for idx, row in df_upload.iterrows():
                    order_d = str(
                        row.get("발주일", datetime.date.today())
                    ).split(" ")[0]
                    delivery_d = str(
                        row.get("납품희망일", order_d)
                    ).split(" ")[0]
                    io_type = str(row.get("구분(입고/출고)", "출고")).strip()
                    purpose = str(
                        row.get("용도(납품/매입/샘플/FOC/집기출고)", "납품")
                    ).strip()
                    p_name = str(row.get("상품명", "")).strip()
                    qty = int(row.get("수량", 0))
                    client = str(row.get("거래처명", "-")).strip()
                    dest = str(row.get("납품처명", "-")).strip()
                    wh = str(row.get("창고명", "SAGAWA")).strip()
                    o_no = str(row.get("발주번호", "-")).strip()
                    o_code = str(row.get("발주관리코드", "-")).strip()
                    status = str(row.get("상태", "완료")).strip()

                    matched_p = next(
                        (p for p in master_prods if p["product_name"] == p_name),
                        None,
                    )
                    matched_f = next(
                        (f for f in master_fixs if f["fixture_name"] == p_name),
                        None,
                    )

                    if matched_p:
                        item_cat = "제품"
                        jan_code = matched_p.get(
                            "box_jan_code", matched_p.get("jan_code", "")
                        )
                        units_per_box = matched_p.get("units_per_box", 1)
                        box_qty = round(qty / units_per_box, 2)

                        if purpose in ["납품", "매입"]:
                            custom_p = next(
                                (
                                    cp
                                    for cp in client_prods
                                    if cp["client_name"] == client
                                    and cp.get("product_name") == p_name
                                ),
                                None,
                            )
                            unit_price = (
                                custom_p["custom_supply_price"]
                                if custom_p
                                else matched_p.get("supply_price_jpy", 0)
                            )
                        else:
                            unit_price = 0

                    elif matched_f:
                        item_cat = "집기"
                        jan_code = "-"
                        box_qty = 0
                        unit_price = 0
                    else:
                        item_cat = "제품"
                        jan_code = "-"
                        box_qty = qty
                        unit_price = 0

                    total_amount = unit_price * qty

                    st.session_state.stock_logs.append({
                        "date": order_d,
                        "delivery_date": delivery_d,
                        "type": io_type,
                        "item_category": item_cat,
                        "purpose": purpose,
                        "jan_code": jan_code,
                        "product_name": p_name,
                        "qty": qty,
                        "box_qty": box_qty,
                        "unit_price": unit_price,
                        "total_amount": total_amount,
                        "warehouse": wh,
                        "order_no": o_no,
                        "order_code": o_code,
                        "status": status,
                        "client_name": client,
                        "destination": dest,
                        "worker": user["name"] if user else t["worker_excel"],
                    })

                    if item_cat == "제품":
                        stk = next(
                            (
                                s
                                for s in st.session_state.warehouse_stocks
                                if s["warehouse"] == wh
                                and (
                                    s["jan_code"] == jan_code
                                    or s["product_name"] == p_name
                                )
                            ),
                            None,
                        )
                        if io_type == "입고":
                            if stk:
                                stk["stock_qty"] += qty
                            else:
                                st.session_state.warehouse_stocks.append({
                                    "warehouse": wh,
                                    "jan_code": jan_code,
                                    "product_name": p_name,
                                    "stock_qty": qty,
                                })
                        elif io_type == "출고":
                            if stk:
                                stk["stock_qty"] -= qty

                    success_count += 1

            st.success(t["msg_excel_success"].format(success_count))
            st.rerun()

        except Exception as e:
            st.error(f"{t['msg_excel_err']} {e}")
