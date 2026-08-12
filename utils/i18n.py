import streamlit as st

I18N = {
    "KO": {
        "title": "ERP 시스템",
        "lang_select": "언어 선택 / Language",
        # 좌측 메뉴 카테고리
        "nav_dashboard": "📊 메인 대시보드",
        "nav_master": "⚙️ 마스터 관리 (제품/거래처)",
        "nav_order": "📦 출고/납품 작성 (최대 30개)",
        "nav_inventory": "🏢 창고별 재고 및 위탁 현황",
        "nav_hr": "⏰ 근태 및 인사 관리",
        
        # 대시보드
        "dashboard_title": "📊 매출 Analytics & 대시보드",
        "tab_monthly": "📅 월별 조회 (연도/월)",
        "tab_detail": "🔍 상세 기간 조회 (프셋 선택)",
        "select_year": "연도 선택",
        "select_month": "월 선택",
        "preset_select": "조회 기간 프셋",
        "preset_1d": "1일 (오늘)",
        "preset_1w": "1주일",
        "preset_1m": "1달",
        "preset_1y": "1년",
        "preset_custom": "직접 범위 지정",
        
        # 출고 / 납품
        "order_title": "📦 출고 및 납품 작성",
        "order_no": "발주번호",
        "partner_select": "거래처 선택",
        "delivery_dest": "납품처 정보",
        "deliv_name": "납품처명",
        "deliv_zip": "우편번호",
        "deliv_addr": "주소",
        "deliv_phone": "전화번호",
        "order_date": "발주일",
        "delivery_date": "납품지정일",
        "wh_select": "출고창고 선택",
        "item_list": "납품 제품 목록 (최대 30개)",
        "unit_price": "공급단가 (JPY)",
        "qty": "수량",
        "box_qty": "Box 수량",
        "total_amount": "공급가 (JPY)",
        "grand_total_qty": "최종 총 발주량",
        "grand_total_amount": "최종 총 공급가액 (JPY, VAT별도)",
        "submit_order": "🚀 발주 및 출고 등록",
        "no_stock_warn": "선택한 창고에 재고가 있는 거래처 등록 제품만 표시됩니다."
    },
    "JA": {
        "title": "ERP システム",
        "lang_select": "言語選択 / Language",
        "nav_dashboard": "📊 メインダッシュボード",
        "nav_master": "⚙️ マスタ管理 (商品/取引先)",
        "nav_order": "📦 出荷・納品作成 (最大30件)",
        "nav_inventory": "🏢 倉庫別在庫・委託状況",
        "nav_hr": "⏰ 勤怠・人事管理",
        
        "dashboard_title": "📊 売上アナリティクス & ダッシュボード",
        "tab_monthly": "📅 月別照会 (年/月)",
        "tab_detail": "🔍 詳細期間照会 (プリセット)",
        "select_year": "年選択",
        "select_month": "月選択",
        "preset_select": "照会期間プリセット",
        "preset_1d": "1日 (本日)",
        "preset_1w": "1週間",
        "preset_1m": "1ヶ月",
        "preset_1y": "1年",
        "preset_custom": "直接指定",
        
        "order_title": "📦 出荷・納品作成",
        "order_no": "発注番号",
        "partner_select": "取引先選択",
        "delivery_dest": "納品先情報",
        "deliv_name": "納品先名",
        "deliv_zip": "郵便番号",
        "deliv_addr": "住所",
        "deliv_phone": "電話番号",
        "order_date": "発注日",
        "delivery_date": "納品指定日",
        "wh_select": "出荷倉庫選択",
        "item_list": "納品商品リスト (最大30件)",
        "unit_price": "供給単価 (JPY)",
        "qty": "数量",
        "box_qty": "Box 数量",
        "total_amount": "供給価額 (JPY)",
        "grand_total_qty": "最終総発注量",
        "grand_total_amount": "最終総供給金額 (JPY, VAT別)",
        "submit_order": "🚀 発注・出荷登録",
        "no_stock_warn": "選択した倉庫に在庫がある取引先登録商品のみ表示されます。"
    },
    "EN": {
        "title": "ERP System",
        "lang_select": "Language",
        "nav_dashboard": "📊 Main Dashboard",
        "nav_master": "⚙️ Master Management",
        "nav_order": "📦 Delivery Order (Max 30)",
        "nav_inventory": "🏢 Inventory & Consignment",
        "nav_hr": "⏰ HR Management",
        
        "dashboard_title": "📊 Sales Analytics & Dashboard",
        "tab_monthly": "📅 Monthly View (Year/Month)",
        "tab_detail": "🔍 Detailed Date Range (Presets)",
        "select_year": "Select Year",
        "select_month": "Select Month",
        "preset_select": "Date Range Preset",
        "preset_1d": "1 Day (Today)",
        "preset_1w": "1 Week",
        "preset_1m": "1 Month",
        "preset_1y": "1 Year",
        "preset_custom": "Custom Range",
        
        "order_title": "📦 Delivery Order Entry",
        "order_no": "Order No.",
        "partner_select": "Select Partner",
        "delivery_dest": "Delivery Destination",
        "deliv_name": "Recipient Name",
        "deliv_zip": "Zipcode",
        "deliv_addr": "Address",
        "deliv_phone": "Phone Number",
        "order_date": "Order Date",
        "delivery_date": "Delivery Date",
        "wh_select": "Source Warehouse",
        "item_list": "Product Items (Max 30)",
        "unit_price": "Unit Price (JPY)",
        "qty": "Quantity",
        "box_qty": "Box Count",
        "total_amount": "Supply Total (JPY)",
        "grand_total_qty": "Grand Total Qty",
        "grand_total_amount": "Grand Total Amount (JPY, Excl. VAT)",
        "submit_order": "🚀 Submit Order",
        "no_stock_warn": "Only displays partner products with available stock in selected warehouse."
    }
}

def get_lang():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "KO"
    return st.session_state["lang"]

def t(key):
    lang = get_lang()
    return I18N.get(lang, {}).get(key, I18N["KO"].get(key, key))

# 언어 선택 드롭다운 (key 추가로 Duplicate Element ID 방지)
def render_lang_selector():
    lang_options = {"한국어": "KO", "日本語": "JA", "English": "EN"}
    current_lang = get_lang()
    current_label = [k for k, v in lang_options.items() if v == current_lang][0]
    
    selected = st.sidebar.selectbox(
        t("lang_select"),
        options=list(lang_options.keys()),
        index=list(lang_options.keys()).index(current_label),
        key="global_sidebar_lang_selector"  # 고유 키 지정
    )
    if lang_options[selected] != current_lang:
        st.session_state["lang"] = lang_options[selected]
        st.rerun()

# 언어 선택 + 카테고리 사이드바 통합 출력
def render_sidebar():
    st.sidebar.title(t("title"))
    render_lang_selector()
