import streamlit as st
import pandas as pd
from datetime import datetime
import json

# ==========================================
# 0. PAGE CONFIG & DESIGN SYSTEM INIT
# ==========================================
st.set_page_config(
    page_title="Enterprise Integrated ERP System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem; }
    .sub-title { font-size: 1.2rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. TRANSLATION DICTIONARY (한국어 / 日本語 / English)
# ==========================================
I18N = {
    "한국어": {
        "title": "🏢 통합 ERP 시스템",
        "lang_select": "🌐 언어 선택 / Language",
        "menu": {
            "dashboard": "Dashboard (대시보드)",
            "master_data": "Master Data (기준 정보)",
            "purchase": "Purchase Management (구매 관리)",
            "inventory": "Inventory Management (재고 관리)",
            "sales": "Sales Management (판매 관리)",
            "ec": "EC Management (EC 매출 관리)",
            "settlement": "Settlement (정산 관리)",
            "system": "System Administration (시스템 관리)"
        },
        "dashboard": {
            "title": "경영진 종합 대시보드",
            "kpi_sales": "이번 달 B2B 매출",
            "kpi_unbilled": "미청구 금액",
            "kpi_ec": "이번 달 EC 매출",
            "kpi_po": "진행 중 구매 건수",
            "stock_overview": "재고 현황 요약",
            "audit_logs": "최근 감사 로그"
        },
        "master": {
            "title": "기준 정보 관리",
            "tab_cust": "거래처 (Customers)",
            "tab_supp": "공급처 (Suppliers)",
            "tab_prod": "상품 (Products)",
            "tab_wh": "창고 (Warehouses)",
            "code": "코드",
            "name": "이름/회사명",
            "currency": "통화",
            "sku": "SKU 번호",
            "unit_price": "판매가",
            "cost_price": "매입가",
            "btn_add": "등록하기"
        },
        "purchase": {
            "title": "구매 및 입고 관리",
            "rule_warning": "⚠️ 절대 규칙: 공급처 PO 번호는 자동으로 생성되지 않으며, 공급처가 발행한 번호를 수동 입력해야 합니다.",
            "tab_req": "구매 요청 (Request)",
            "tab_po": "구매 발주 (Order)",
            "tab_rec": "입고 처리 (Receiving)",
            "supp_po_no": "공급처 발주번호 (필수)",
            "btn_po_submit": "구매 발주 등록",
            "btn_receive": "입고 완료 (COMPLETED)",
            "dup_error": "중복 오류: 해당 공급처에 동일한 PO 번호가 이미 존재합니다."
        },
        "inventory": {
            "title": "재고 통합 관리",
            "tab_overview": "현재 재고 현황",
            "tab_transfer": "창고간 재고 이동",
            "tab_history": "재고 변경 이력 (Transactions)",
            "from_wh": "출발 창고",
            "to_wh": "도착 창고",
            "transfer_qty": "이동 수량",
            "btn_transfer": "재고 이동 실행",
            "err_stock": "출발 창고의 재고가 부족합니다."
        },
        "sales": {
            "title": "판매 및 납품/청구 관리",
            "rule_warning": "⚠️ 절대 규칙: 거래처 PO 번호는 수동 입력해야 합니다.",
            "tab_order": "거래처 발주 (Order)",
            "tab_delivery": "납품 처리 (Delivery)",
            "tab_invoice": "월 합산 청구 (Invoice)",
            "cust_po_no": "거래처 PO 번호 (필수)",
            "trans_type": "거래 유형 (NORMAL/FOC/SAMPLE)",
            "shipping_opt": "배송비 구분",
            "shipping_fee": "배송비 금액",
            "btn_delivery": "납품 완료 (COMPLETED)",
            "btn_invoice": "월 합산 Invoice 발행"
        },
        "ec": {
            "title": "EC 플랫폼 매출 관리 (수동 입력)",
            "platform": "EC 플랫폼",
            "account": "계정명",
            "amount": "매출 금액",
            "btn_save": "EC 매출 저장"
        },
        "settlement": {
            "title": "정산 및 미수금 관리",
            "btn_pay": "입금 완료 처리 (PAID)"
        },
        "system": {
            "title": "시스템 관리 및 Audit Log",
            "tab_role": "사용자 권한 (Roles)",
            "tab_audit": "감사 로그 (Audit Log)"
        }
    },
    "日本語": {
        "title": "🏢 統合 ERP システム",
        "lang_select": "🌐 言語選択 / Language",
        "menu": {
            "dashboard": "Dashboard (ダッシュボード)",
            "master_data": "Master Data (マスタ管理)",
            "purchase": "Purchase Management (購買・入荷管理)",
            "inventory": "Inventory Management (在庫管理)",
            "sales": "Sales Management (販売・納품管理)",
            "ec": "EC Management (EC売上管理)",
            "settlement": "Settlement (精算管理)",
            "system": "System Administration (システム管理)"
        },
        "dashboard": {
            "title": "経営陣総合ダッシュボード",
            "kpi_sales": "今月のB2B売上",
            "kpi_unbilled": "未請求金額",
            "kpi_ec": "今月のEC売上",
            "kpi_po": "進行中の購買件数",
            "stock_overview": "在庫状況サマリー",
            "audit_logs": "最近の監査ログ"
        },
        "master": {
            "title": "マスタデータ管理",
            "tab_cust": "取引先 (Customers)",
            "tab_supp": "仕入先 (Suppliers)",
            "tab_prod": "商品 (Products)",
            "tab_wh": "倉庫 (Warehouses)",
            "code": "コード",
            "name": "名前/会社名",
            "currency": "通貨",
            "sku": "SKU番号",
            "unit_price": "販売単価",
            "cost_price": "仕入単価",
            "btn_add": "登録する"
        },
        "purchase": {
            "title": "購買および入荷管理",
            "rule_warning": "⚠️ 絶対ルール: 仕入先PO番号は自動生成されません。仕入先が発行した番号を手動入力してください。",
            "tab_req": "購買依頼 (Request)",
            "tab_po": "発注管理 (Order)",
            "tab_rec": "入荷処理 (Receiving)",
            "supp_po_no": "仕入先PO番号 (必須)",
            "btn_po_submit": "購買発注登録",
            "btn_receive": "入荷完了 (COMPLETED)",
            "dup_error": "重複エラー: 該当仕入先に同一のPO番号が既に存在します。"
        },
        "inventory": {
            "title": "在庫統合管理",
            "tab_overview": "現在の在庫状況",
            "tab_transfer": "倉庫間在庫移動",
            "tab_history": "在庫変動履歴 (Transactions)",
            "from_wh": "移動元倉庫",
            "to_wh": "移動先倉庫",
            "transfer_qty": "移動数量",
            "btn_transfer": "在庫移動実行",
            "err_stock": "移動元倉庫の在庫が不足しています。"
        },
        "sales": {
            "title": "販売および納品・請求管理",
            "rule_warning": "⚠️ 絶対ルール: 取引先PO番号は手動入力する必要があります。",
            "tab_order": "受注管理 (Order)",
            "tab_delivery": "納品処理 (Delivery)",
            "tab_invoice": "月次合算請求 (Invoice)",
            "cust_po_no": "取引先PO番号 (必須)",
            "trans_type": "取引タイプ (NORMAL/FOC/SAMPLE)",
            "shipping_opt": "送料区分",
            "shipping_fee": "送料金額",
            "btn_delivery": "納品完了 (COMPLETED)",
            "btn_invoice": "月次合算Invoice発行"
        },
        "ec": {
            "title": "ECプラットフォーム売上管理 (手動入力)",
            "platform": "ECプラットフォーム",
            "account": "アカウント名",
            "amount": "売上金額",
            "btn_save": "EC売上保存"
        },
        "settlement": {
            "title": "精算および売掛金管理",
            "btn_pay": "入金完了処理 (PAID)"
        },
        "system": {
            "title": "システム管理およびAudit Log",
            "tab_role": "ユーザー権限 (Roles)",
            "tab_audit": "監査ログ (Audit Log)"
        }
    },
    "English": {
        "title": "🏢 Integrated ERP System",
        "lang_select": "🌐 Language Selection",
        "menu": {
            "dashboard": "Dashboard",
            "master_data": "Master Data",
            "purchase": "Purchase Management",
            "inventory": "Inventory Management",
            "sales": "Sales Management",
            "ec": "EC Management",
            "settlement": "Settlement",
            "system": "System Administration"
        },
        "dashboard": {
            "title": "Executive Dashboard",
            "kpi_sales": "Monthly B2B Sales",
            "kpi_unbilled": "Unbilled Amount",
            "kpi_ec": "Monthly EC Revenue",
            "kpi_po": "Active POs",
            "stock_overview": "Inventory Overview",
            "audit_logs": "Recent Audit Logs"
        },
        "master": {
            "title": "Master Data Management",
            "tab_cust": "Customers",
            "tab_supp": "Suppliers",
            "tab_prod": "Products",
            "tab_wh": "Warehouses",
            "code": "Code",
            "name": "Name/Company",
            "currency": "Currency",
            "sku": "SKU Number",
            "unit_price": "Selling Price",
            "cost_price": "Purchase Cost",
            "btn_add": "Register"
        },
        "purchase": {
            "title": "Purchase & Receiving Management",
            "rule_warning": "⚠️ Absolute Rule: Supplier PO Number MUST be entered manually.",
            "tab_req": "Purchase Request",
            "tab_po": "Purchase Order",
            "tab_rec": "Receiving",
            "supp_po_no": "Supplier PO No (Mandatory)",
            "btn_po_submit": "Submit Order",
            "btn_receive": "Complete Receiving",
            "dup_error": "Duplicate Error: Supplier PO Number already exists."
        },
        "inventory": {
            "title": "Inventory Management",
            "tab_overview": "Current Stock Status",
            "tab_transfer": "Stock Transfer",
            "tab_history": "Stock Transactions",
            "from_wh": "Origin Warehouse",
            "to_wh": "Destination Warehouse",
            "transfer_qty": "Transfer Quantity",
            "btn_transfer": "Execute Transfer",
            "err_stock": "Insufficient stock in origin warehouse."
        },
        "sales": {
            "title": "Sales & Invoice Management",
            "rule_warning": "⚠️ Absolute Rule: Customer PO Number MUST be entered manually.",
            "tab_order": "Customer Order",
            "tab_delivery": "Delivery Processing",
            "tab_invoice": "Monthly Invoice",
            "cust_po_no": "Customer PO No (Mandatory)",
            "trans_type": "Transaction Type (NORMAL/FOC/SAMPLE)",
            "shipping_opt": "Shipping Option",
            "shipping_fee": "Shipping Fee Amount",
            "btn_delivery": "Complete Delivery",
            "btn_invoice": "Issue Monthly Invoice"
        },
        "ec": {
            "title": "EC Platform Sales Management",
            "platform": "EC Platform",
            "account": "Account Name",
            "amount": "Sales Amount",
            "btn_save": "Save Record"
        },
        "settlement": {
            "title": "Settlement & Receivables",
            "btn_pay": "Mark as PAID"
        },
        "system": {
            "title": "System Admin & Audit Logs",
            "tab_role": "Roles & Permissions",
            "tab_audit": "Audit Logs"
        }
    }
}

# ==========================================
# 2. SESSION STATE & DATA INITIALIZATION
# ==========================================
def init_session():
    if 'audit_logs' not in st.session_state:
        st.session_state.audit_logs = []
    if 'db_customers' not in st.session_state:
        st.session_state.db_customers = pd.DataFrame([
            {"id": 1, "code": "CUST-001", "name": "Global Retail Co", "currency": "USD", "is_active": True},
            {"id": 2, "code": "CUST-002", "name": "Tokyo Trading Ltd", "currency": "JPY", "is_active": True}
        ])
    if 'db_suppliers' not in st.session_state:
        st.session_state.db_suppliers = pd.DataFrame([
            {"id": 1, "code": "SUP-001", "name": "Primary Logistics Corp", "currency": "USD", "is_active": True}
        ])
    if 'db_products' not in st.session_state:
        st.session_state.db_products = pd.DataFrame([
            {"id": 1, "sku": "SKU-A100", "name": "Wireless Mouse", "unit_price": 50, "purchase_price": 25, "is_active": True},
            {"id": 2, "sku": "SKU-B200", "name": "Mechanical Keyboard", "unit_price": 120, "purchase_price": 60, "is_active": True}
        ])
    if 'db_warehouses' not in st.session_state:
        st.session_state.db_warehouses = pd.DataFrame([
            {"id": 1, "name": "Main Warehouse Tokyo", "location": "Tokyo", "is_active": True},
            {"id": 2, "name": "Sub Warehouse Osaka", "location": "Osaka", "is_active": True}
        ])
    if 'db_inventory' not in st.session_state:
        st.session_state.db_inventory = pd.DataFrame([
            {"warehouse_id": 1, "product_id": 1, "current_stock": 500, "reserved_stock": 50},
            {"warehouse_id": 1, "product_id": 2, "current_stock": 200, "reserved_stock": 20}
        ])
    if 'db_stock_transactions' not in st.session_state:
        st.session_state.db_stock_transactions = []
    if 'db_purchase_orders' not in st.session_state:
        st.session_state.db_purchase_orders = []
    if 'db_deliveries' not in st.session_state:
        st.session_state.db_deliveries = []
    if 'db_sales_orders' not in st.session_state:
        st.session_state.db_sales_orders = []
    if 'db_invoices' not in st.session_state:
        st.session_state.db_invoices = []
    if 'db_ec_sales' not in st.session_state:
        st.session_state.db_ec_sales = []

init_session()

def log_audit(user_id, target_table, record_id, event, before_data=None, after_data=None):
    st.session_state.audit_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "event": event,
        "target_table": target_table,
        "record_id": record_id,
        "before_data": json.dumps(before_data) if before_data else None,
        "after_data": json.dumps(after_data) if after_data else None
    })

# ==========================================
# 3. SIDEBAR: LANGUAGE & SINGLE MENU
# ==========================================
st.sidebar.title("🏢 Integrated ERP")

# Language Selector
selected_lang = st.sidebar.selectbox("🌐 Language / 언어", ["한국어", "日本語", "English"])
txt = I18N[selected_lang]

st.sidebar.markdown("---")

# Single Unified Navigation (8 Categories)
menu_keys = [
    ("dashboard", txt["menu"]["dashboard"]),
    ("master_data", txt["menu"]["master_data"]),
    ("purchase", txt["menu"]["purchase"]),
    ("inventory", txt["menu"]["inventory"]),
    ("sales", txt["menu"]["sales"]),
    ("ec", txt["menu"]["ec"]),
    ("settlement", txt["menu"]["settlement"]),
    ("system", txt["menu"]["system"])
]

selected_menu_label = st.sidebar.radio("Navigation", [m[1] for m in menu_keys])
selected_menu_key = next(m[0] for m in menu_keys if m[1] == selected_menu_label)

st.sidebar.markdown("---")
st.sidebar.caption("Current User: admin@company.com (Role: ADMIN)")

# ==========================================
# 4. CATEGORY VIEWS
# ==========================================

# --- [4-1. DASHBOARD] ---
if selected_menu_key == "dashboard":
    st.markdown(f"<div class='main-title'>{txt['dashboard']['title']}</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=txt['dashboard']['kpi_sales'], value="$124,500", delta="+12%")
    with col2:
        st.metric(label=txt['dashboard']['kpi_unbilled'], value="$18,200", delta="-3%")
    with col3:
        st.metric(label=txt['dashboard']['kpi_ec'], value="¥2,450,000", delta="+8%")
    with col4:
        st.metric(label=txt['dashboard']['kpi_po'], value="4 Orders", delta="2 Inbound")
        
    st.markdown("---")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.subheader(txt['dashboard']['stock_overview'])
        st.dataframe(st.session_state.db_inventory, use_container_width=True)
    with d_col2:
        st.subheader(txt['dashboard']['audit_logs'])
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)

# --- [4-2. MASTER DATA] ---
elif selected_menu_key == "master_data":
    st.markdown(f"<div class='main-title'>{txt['master']['title']}</div>", unsafe_allow_html=True)
    sub_tab = st.tabs([txt['master']['tab_cust'], txt['master']['tab_supp'], txt['master']['tab_prod'], txt['master']['tab_wh']])
    
    with sub_tab[0]: # Customers
        st.dataframe(st.session_state.db_customers[st.session_state.db_customers['is_active']], use_container_width=True)
        with st.expander(txt['master']['btn_add']):
            with st.form("cust_form"):
                c_code = st.text_input(txt['master']['code'])
                c_name = st.text_input(txt['master']['name'])
                c_curr = st.selectbox(txt['master']['currency'], ["USD", "JPY", "KRW"])
                if st.form_submit_button(txt['master']['btn_add']) and c_code and c_name:
                    new_id = len(st.session_state.db_customers) + 1
                    row = {"id": new_id, "code": c_code, "name": c_name, "currency": c_curr, "is_active": True}
                    st.session_state.db_customers = pd.concat([st.session_state.db_customers, pd.DataFrame([row])], ignore_index=True)
                    log_audit("admin", "Customer", new_id, "CREATE", None, row)
                    st.rerun()

    with sub_tab[1]: # Suppliers
        st.dataframe(st.session_state.db_suppliers[st.session_state.db_suppliers['is_active']], use_container_width=True)

    with sub_tab[2]: # Products
        st.dataframe(st.session_state.db_products[st.session_state.db_products['is_active']], use_container_width=True)

    with sub_tab[3]: # Warehouses
        st.dataframe(st.session_state.db_warehouses[st.session_state.db_warehouses['is_active']], use_container_width=True)

# --- [4-3. PURCHASE MANAGEMENT] ---
elif selected_menu_key == "purchase":
    st.markdown(f"<div class='main-title'>{txt['purchase']['title']}</div>", unsafe_allow_html=True)
    p_tab = st.tabs([txt['purchase']['tab_req'], txt['purchase']['tab_po'], txt['purchase']['tab_rec']])
    
    with p_tab[1]: # PO
        st.warning(txt['purchase']['rule_warning'])
        with st.form("po_form"):
            supp_id = st.selectbox("Supplier", st.session_state.db_suppliers['id'].tolist(), 
                                   format_func=lambda x: st.session_state.db_suppliers.loc[st.session_state.db_suppliers['id']==x, 'name'].values[0])
            supp_po_no = st.text_input(txt['purchase']['supp_po_no'])
            prod_id = st.selectbox("Product", st.session_state.db_products['id'].tolist(),
                                   format_func=lambda x: st.session_state.db_products.loc[st.session_state.db_products['id']==x, 'name'].values[0])
            qty = st.number_input("Quantity", min_value=1, value=100)
            
            if st.form_submit_button(txt['purchase']['btn_po_submit']):
                duplicate = any((po['supplier_id'] == supp_id and po['supplier_po_no'] == supp_po_no) for po in st.session_state.db_purchase_orders)
                if not supp_po_no:
                    st.error("Error: Supplier PO No required")
                elif duplicate:
                    st.error(txt['purchase']['dup_error'])
                else:
                    po_id = len(st.session_state.db_purchase_orders) + 1
                    po_data = {"id": po_id, "supplier_id": supp_id, "supplier_po_no": supp_po_no, "product_id": prod_id, "quantity": qty, "status": "APPROVED"}
                    st.session_state.db_purchase_orders.append(po_data)
                    log_audit("admin", "PurchaseOrder", po_id, "CREATE", None, po_data)
                    st.rerun()

        st.dataframe(pd.DataFrame(st.session_state.db_purchase_orders), use_container_width=True)

    with p_tab[2]: # Receiving
        open_pos = [po for po in st.session_state.db_purchase_orders if po['status'] == 'APPROVED']
        if open_pos:
            selected_po_id = st.selectbox("Select PO", [po['id'] for po in open_pos], format_func=lambda x: f"PO: {[po['supplier_po_no'] for po in open_pos if po['id']==x][0]}")
            target_po = next(po for po in open_pos if po['id'] == selected_po_id)
            wh_id = st.selectbox("Warehouse", st.session_state.db_warehouses['id'].tolist())
            
            if st.button(txt['purchase']['btn_receive']):
                target_po['status'] = 'COMPLETED'
                inv_df = st.session_state.db_inventory
                mask = (inv_df['warehouse_id'] == wh_id) & (inv_df['product_id'] == target_po['product_id'])
                if mask.any():
                    st.session_state.db_inventory.loc[mask, 'current_stock'] += target_po['quantity']
                else:
                    st.session_state.db_inventory = pd.concat([st.session_state.db_inventory, pd.DataFrame([{"warehouse_id": wh_id, "product_id": target_po['product_id'], "current_stock": target_po['quantity'], "reserved_stock": 0}])], ignore_index=True)
                
                tx = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "type": "INBOUND", "warehouse_id": wh_id, "product_id": target_po['product_id'], "quantity": target_po['quantity'], "reference_no": target_po['supplier_po_no']}
                st.session_state.db_stock_transactions.append(tx)
                log_audit("admin", "Receiving", target_po['id'], "RECEIVE", None, tx)
                st.rerun()

# --- [4-4. INVENTORY MANAGEMENT] ---
elif selected_menu_key == "inventory":
    st.markdown(f"<div class='main-title'>{txt['inventory']['title']}</div>", unsafe_allow_html=True)
    i_tab = st.tabs([txt['inventory']['tab_overview'], txt['inventory']['tab_transfer'], txt['inventory']['tab_history']])
    
    with i_tab[0]:
        st.dataframe(st.session_state.db_inventory, use_container_width=True)
        
    with i_tab[1]:
        col1, col2 = st.columns(2)
        with col1:
            from_wh = st.selectbox(txt['inventory']['from_wh'], st.session_state.db_warehouses['id'].tolist())
        with col2:
            to_wh = st.selectbox(txt['inventory']['to_wh'], [w for w in st.session_state.db_warehouses['id'].tolist() if w != from_wh])
        p_id = st.selectbox("Product", st.session_state.db_products['id'].tolist())
        t_qty = st.number_input(txt['inventory']['transfer_qty'], min_value=1, value=10)
        
        if st.button(txt['inventory']['btn_transfer']):
            inv_df = st.session_state.db_inventory
            f_mask = (inv_df['warehouse_id'] == from_wh) & (inv_df['product_id'] == p_id)
            if not f_mask.any() or inv_df.loc[f_mask, 'current_stock'].values[0] < t_qty:
                st.error(txt['inventory']['err_stock'])
            else:
                st.session_state.db_inventory.loc[f_mask, 'current_stock'] -= t_qty
                t_mask = (inv_df['warehouse_id'] == to_wh) & (inv_df['product_id'] == p_id)
                if t_mask.any():
                    st.session_state.db_inventory.loc[t_mask, 'current_stock'] += t_qty
                else:
                    st.session_state.db_inventory = pd.concat([st.session_state.db_inventory, pd.DataFrame([{"warehouse_id": to_wh, "product_id": p_id, "current_stock": t_qty, "reserved_stock": 0}])], ignore_index=True)
                
                tx = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "type": "TRANSFER", "warehouse_id": f"{from_wh}->{to_wh}", "product_id": p_id, "quantity": t_qty, "reference_no": "TRANSFER"}
                st.session_state.db_stock_transactions.append(tx)
                log_audit("admin", "Inventory", 0, "TRANSFER", None, tx)
                st.rerun()

    with i_tab[2]:
        st.dataframe(pd.DataFrame(st.session_state.db_stock_transactions), use_container_width=True)

# --- [4-5. SALES MANAGEMENT] ---
elif selected_menu_key == "sales":
    st.markdown(f"<div class='main-title'>{txt['sales']['title']}</div>", unsafe_allow_html=True)
    s_tab = st.tabs([txt['sales']['tab_order'], txt['sales']['tab_delivery'], txt['sales']['tab_invoice']])
    
    with s_tab[0]:
        st.warning(txt['sales']['rule_warning'])
        with st.form("so_form"):
            c_id = st.selectbox("Customer", st.session_state.db_customers['id'].tolist(), format_func=lambda x: st.session_state.db_customers.loc[st.session_state.db_customers['id']==x, 'name'].values[0])
            c_po = st.text_input(txt['sales']['cust_po_no'])
            p_id = st.selectbox("Product", st.session_state.db_products['id'].tolist(), format_func=lambda x: st.session_state.db_products.loc[st.session_state.db_products['id']==x, 'name'].values[0])
            o_qty = st.number_input("Quantity", min_value=1, value=50)
            
            if st.form_submit_button("Create Sales Order"):
                duplicate = any((so['customer_id'] == c_id and so['customer_po_no'] == c_po) for so in st.session_state.db_sales_orders)
                if not c_po:
                    st.error("Error: Customer PO required")
                elif duplicate:
                    st.error("Duplicate Customer PO detected")
                else:
                    so_id = len(st.session_state.db_sales_orders) + 1
                    u_price = st.session_state.db_products.loc[st.session_state.db_products['id']==p_id, 'unit_price'].values[0]
                    so_data = {"id": so_id, "customer_id": c_id, "customer_po_no": c_po, "product_id": p_id, "quantity": o_qty, "unit_price": u_price, "status": "APPROVED"}
                    st.session_state.db_sales_orders.append(so_data)
                    log_audit("admin", "SalesOrder", so_id, "CREATE", None, so_data)
                    st.rerun()

        st.dataframe(pd.DataFrame(st.session_state.db_sales_orders), use_container_width=True)

    with s_tab[1]: # Delivery
        open_sos = [so for so in st.session_state.db_sales_orders if so['status'] == 'APPROVED']
        if open_sos:
            so_id_sel = st.selectbox("Select Order", [so['id'] for so in open_sos], format_func=lambda x: f"SO: {[so['customer_po_no'] for so in open_sos if so['id']==x][0]}")
            target_so = next(so for so in open_sos if so['id'] == so_id_sel)
            wh_id = st.selectbox("Dispatch Warehouse", st.session_state.db_warehouses['id'].tolist())
            d_qty = st.number_input("Delivery Quantity", min_value=1, max_value=target_so['quantity'], value=target_so['quantity'])
            
            trans_type = st.selectbox(txt['sales']['trans_type'], ["NORMAL", "FOC", "SAMPLE"])
            ship_opt = st.radio(txt['sales']['shipping_opt'], ["FREE", "PAID"])
            ship_fee = st.number_input(txt['sales']['shipping_fee'], min_value=0, value=0 if ship_opt=="FREE" else 5000)
            
            if st.button(txt['sales']['btn_delivery']):
                inv_df = st.session_state.db_inventory
                mask = (inv_df['warehouse_id'] == wh_id) & (inv_df['product_id'] == target_so['product_id'])
                if not mask.any() or inv_df.loc[mask, 'current_stock'].values[0] < d_qty:
                    st.error("Insufficient stock!")
                else:
                    st.session_state.db_inventory.loc[mask, 'current_stock'] -= d_qty
                    tx = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "type": "OUTBOUND", "warehouse_id": wh_id, "product_id": target_so['product_id'], "quantity": d_qty, "reference_no": target_so['customer_po_no']}
                    st.session_state.db_stock_transactions.append(tx)
                    
                    deliv_id = len(st.session_state.db_deliveries) + 1
                    d_data = {"id": deliv_id, "order_id": target_so['id'], "customer_id": target_so['customer_id'], "product_id": target_so['product_id'], "quantity": d_qty, "unit_price": target_so['unit_price'], "trans_type": trans_type, "shipping_fee": ship_fee, "billed": False}
                    st.session_state.db_deliveries.append(d_data)
                    log_audit("admin", "Delivery", deliv_id, "COMPLETE", None, d_data)
                    st.rerun()

        st.dataframe(pd.DataFrame(st.session_state.db_deliveries), use_container_width=True)

    with s_tab[2]: # Invoice
        unbilled = [d for d in st.session_state.db_deliveries if not d['billed']]
        if unbilled:
            df_unbilled = pd.DataFrame(unbilled)
            st.dataframe(df_unbilled, use_container_width=True)
            target_c = st.selectbox("Select Customer for Invoice", df_unbilled['customer_id'].unique())
            
            if st.button(txt['sales']['btn_invoice']):
                c_delivs = [d for d in unbilled if d['customer_id'] == target_c]
                merch_amt = sum(d['quantity'] * d['unit_price'] for d in c_delivs if d['trans_type'] == 'NORMAL')
                ship_amt = sum(d['shipping_fee'] for d in c_delivs)
                
                for d in c_delivs:
                    d['billed'] = True
                    
                inv_id = len(st.session_state.db_invoices) + 1
                inv_data = {"id": inv_id, "customer_id": target_c, "merchandise_amount": merch_amt, "shipping_amount": ship_amt, "total_amount": merch_amt + ship_amt, "status": "ISSUED"}
                st.session_state.db_invoices.append(inv_data)
                log_audit("admin", "Invoice", inv_id, "CREATE", None, inv_data)
                st.rerun()
                
        st.dataframe(pd.DataFrame(st.session_state.db_invoices), use_container_width=True)

# --- [4-6. EC MANAGEMENT] ---
elif selected_menu_key == "ec":
    st.markdown(f"<div class='main-title'>{txt['ec']['title']}</div>", unsafe_allow_html=True)
    with st.form("ec_form"):
        plat = st.selectbox(txt['ec']['platform'], ["Qoo10", "Rakuten", "Amazon JP", "TikTok Shop"])
        acc = st.text_input(txt['ec']['account'], value="Official Store A")
        amt = st.number_input(txt['ec']['amount'], min_value=0, value=15000)
        
        if st.form_submit_button(txt['ec']['btn_save']):
            ec_id = len(st.session_state.db_ec_sales) + 1
            ec_row = {"id": ec_id, "platform": plat, "account": acc, "amount": amt, "date": str(datetime.now().date())}
            st.session_state.db_ec_sales.append(ec_row)
            log_audit("admin", "EC_Sales", ec_id, "CREATE", None, ec_row)
            st.rerun()
            
    st.dataframe(pd.DataFrame(st.session_state.db_ec_sales), use_container_width=True)

# --- [4-7. SETTLEMENT] ---
elif selected_menu_key == "settlement":
    st.markdown(f"<div class='main-title'>{txt['settlement']['title']}</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.db_invoices), use_container_width=True)
    open_invs = [i for i in st.session_state.db_invoices if i['status'] == 'ISSUED']
    if open_invs:
        inv_sel = st.selectbox("Select Invoice", [i['id'] for i in open_invs])
        if st.button(txt['settlement']['btn_pay']):
            target = next(i for i in st.session_state.db_invoices if i['id'] == inv_sel)
            target['status'] = 'PAID'
            log_audit("admin", "Settlement", target['id'], "UPDATE", {"status": "ISSUED"}, {"status": "PAID"})
            st.rerun()

# --- [4-8. SYSTEM ADMINISTRATION] ---
elif selected_menu_key == "system":
    st.markdown(f"<div class='main-title'>{txt['system']['title']}</div>", unsafe_allow_html=True)
    sys_tab = st.tabs([txt['system']['tab_role'], txt['system']['tab_audit']])
    
    with sys_tab[0]:
        st.markdown("- **ADMIN**: Full Access\n- **MANAGER**: Approvals\n- **USER**: Daily Operations\n- **VIEWER**: Read-only")
    with sys_tab[1]:
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
