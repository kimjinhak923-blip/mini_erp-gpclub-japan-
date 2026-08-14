import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# 1. 언어별 번역 딕셔너리 정의 (한국어/일본어/영어)
TRANSLATIONS = {
    "KO": {
        "page_title": "입출고 이력 조회",
        "title": "📜 입출고 통합 이력 조회",
        "no_data": "입출고 이력이 존재하지 않습니다.",
        "type_filter_label": "구분 필터",
        "wh_filter_label": "창고 필터",
        "search_label": "검색어 (상품명, JAN, 거래처)",
        "inbound": "입고",
        "outbound": "출고",
        # 데이터프레임 컬럼 변환 매핑
        "col_date": "일자",
        "col_type": "구분",
        "col_order_no": "주문번호",
        "col_jan_code": "JAN 코드",
        "col_product_name": "상품명",
        "col_qty": "수량",
        "col_unit_price": "단가",
        "col_total_amount": "총금액",
        "col_warehouse": "창고",
        "col_client_name": "거래처명",
        "col_purpose": "용도",
        "col_status": "상태",
    },
    "JA": {
        "page_title": "入出荷履歴照会",
        "title": "📜 入出荷統合履歴照会",
        "no_data": "入出荷履歴が存在しません。",
        "type_filter_label": "区分フィルター",
        "wh_filter_label": "倉庫フィルター",
        "search_label": "検索ワード (商品名, JAN, 取引先)",
        "inbound": "入庫",
        "outbound": "出庫",
        "col_date": "日付",
        "col_type": "区分",
        "col_order_no": "注文番号",
        "col_jan_code": "JANコード",
        "col_product_name": "商品名",
        "col_qty": "数量",
        "col_unit_price": "単価",
        "col_total_amount": "合計金額",
        "col_warehouse": "倉庫",
        "col_client_name": "取引先名",
        "col_purpose": "用途",
        "col_status": "ステータス",
    },
    "EN": {
        "page_title": "Inbound/Outbound History",
        "title": "📜 Integrated Stock Log History",
        "no_data": "No stock logs found.",
        "type_filter_label": "Type Filter",
        "wh_filter_label": "Warehouse Filter",
        "search_label": "Search (Product, JAN, Client)",
        "inbound": "Inbound",
        "outbound": "Outbound",
        "col_date": "Date",
        "col_type": "Type",
        "col_order_no": "Order No.",
        "col_jan_code": "JAN Code",
        "col_product_name": "Product Name",
        "col_qty": "Qty",
        "col_unit_price": "Unit Price",
        "col_total_amount": "Total Amount",
        "col_warehouse": "Warehouse",
        "col_client_name": "Client Name",
        "col_purpose": "Purpose",
        "col_status": "Status",
    },
}

# 2. 현재 선택된 언어 감지 ('lang' 또는 'language' 세션 키 참조)
current_lang = st.session_state.get("lang") or st.session_state.get("language") or "KO"
if current_lang not in TRANSLATIONS:
    current_lang = "KO"

t = TRANSLATIONS[current_lang]

# 3. Streamlit 페이지 설정 (최상단 실행)
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 렌더링 및 사용자 정보 확인
render_sidebar()
user = st.session_state.get("logged_in_user")

# 5. 본문 영역
st.title(t["title"])
st.markdown("---")

if not st.session_state.get("stock_logs"):
    st.info(t["no_data"])
else:
    df_logs = pd.DataFrame(st.session_state.stock_logs)

    # 구분 필터용 옵션 및 매핑 (화면 표시용 <-> 실제 데이터 값 매핑)
    type_options = [t["inbound"], t["outbound"]]
    display_to_real_type = {
        t["inbound"]: "입고",
        t["outbound"]: "출고",
    }

    warehouses_list = st.session_state.get("warehouses", [])

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_display_types = st.multiselect(
            t["type_filter_label"], type_options, default=type_options
        )
    with c2:
        wh_filter = st.multiselect(
            t["wh_filter_label"],
            warehouses_list,
            default=warehouses_list,
        )
    with c3:
        search_kw = st.text_input(t["search_label"], "")

    # 선택된 화면표시 옵션을 실제 데이터 형태("입고", "출고")로 변환
    selected_real_types = [display_to_real_type[dt] for dt in selected_display_types if dt in display_to_real_type]

    # 데이터 필터링
    filtered_df = df_logs[
        (df_logs["type"].isin(selected_real_types)) & (df_logs["warehouse"].isin(wh_filter))
    ]

    if search_kw:
        # 데이터프레임 내 각 컬럼 검색 (존재하지 않을 경우 대비 예외처리 포함)
        cond_prod = filtered_df["product_name"].str.contains(search_kw, na=False) if "product_name" in filtered_df.columns else False
        cond_jan = filtered_df["jan_code"].str.contains(search_kw, na=False) if "jan_code" in filtered_df.columns else False
        cond_cli = filtered_df["client_name"].str.contains(search_kw, na=False) if "client_name" in filtered_df.columns else False
        
        filtered_df = filtered_df[cond_prod | cond_jan | cond_cli]

    # 컬럼명 언어 설정에 맞게 변환
    column_rename_map = {
        "date": t["col_date"],
        "type": t["col_type"],
        "order_no": t["col_order_no"],
        "jan_code": t["col_jan_code"],
        "product_name": t["col_product_name"],
        "qty": t["col_qty"],
        "unit_price": t["col_unit_price"],
        "total_amount": t["col_total_amount"],
        "warehouse": t["col_warehouse"],
        "client_name": t["col_client_name"],
        "purpose": t["col_purpose"],
        "status": t["col_status"],
    }
    
    display_df = filtered_df.rename(columns=column_rename_map)

    st.dataframe(display_df, use_container_width=True)
