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

# Custom CSS for Figma Design System Alignment
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem; }
    .sub-title { font-size: 1.2rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE & SESSION STATE MOCK SETUP
# (Actual implementation connects via Supabase Client)
# ==========================================
def init_session_state():
    # Audit Log Helper
    if 'audit_logs' not in st.session_state:
        st.session_state.audit_logs = []
        
    # Master Data Storage
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
            {"id": 1, "sku": "SKU-A100", "name": "Premium Wireless Mouse", "unit_price": 50, "purchase_price": 25, "is_active": True},
            {"id": 2, "sku": "SKU-B200", "name": "Mechanical Keyboard", "unit_price": 120, "purchase_price": 60, "is_active": True}
        ])
    if 'db_warehouses' not in st.session_state:
        st.session_state.db_warehouses = pd.DataFrame([
            {"id": 1, "name": "Main Warehouse Tokyo", "location": "Tokyo Bay", "is_active": True},
            {"id": 2, "name": "Sub Warehouse Osaka", "location": "Osaka South", "is_active": True}
        ])
        
    # Operational Data Storage
    if 'db_inventory' not in st.session_state:
        st.session_state.db_inventory = pd.DataFrame([
            {"warehouse_id": 1, "product_id": 1, "current_stock": 500, "reserved_stock": 50},
            {"warehouse_id": 1, "product_id": 2, "current_stock": 200, "reserved_stock": 20}
        ])
    if 'db_stock_transactions' not in st.session_state:
        st.session_state.db_stock_transactions = []
    if 'db_purchase_orders' not in st.session_state:
        st.session_state.db_purchase_orders = []
    if 'db_receivings' not in st.session_state:
        st.session_state.db_receivings = []
    if 'db_sales_orders' not in st.session_state:
        st.session_state.db_sales_orders = []
    if 'db_deliveries' not in st.session_state:
        st.session_state.db_deliveries = []
    if 'db_invoices' not in st.session_state:
        st.session_state.db_invoices = []
    if 'db_ec_sales' not in st.session_state:
        st.session_state.db_ec_sales = []

init_session_state()

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
# 2. NAVIGATION (SIDEBAR)
# ==========================================
st.sidebar.title("🏢 Integrated ERP System")

menu_category = st.sidebar.radio(
    "Navigation Categories",
    [
        "Dashboard",
        "Master Data",
        "Purchase Management",
        "Inventory Management",
        "Sales Management",
        "EC Management",
        "Settlement",
        "System Administration"
    ]
)

# User Info Mock in Sidebar
st.sidebar.markdown("---")
st.sidebar.caption("Current User: admin@company.com (Role: ADMIN)")

# ==========================================
# 3. CATEGORY CONTROLLERS
# ==========================================

# --- [3-1. DASHBOARD] ---
if menu_category == "Dashboard":
    st.markdown("<div class='main-title'>System Executive Dashboard</div>", unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total B2B Sales (Monthly)", value="$124,500", delta="+12%")
    with col2:
        st.metric(label="Unbilled Invoices", value="$18,200", delta="-3%")
    with col3:
        st.metric(label="EC Revenue (Monthly)", value="¥2,450,000", delta="+8%")
    with col4:
        st.metric(label="Pending Purchase Orders", value="4 Orders", delta="2 Inbound")
        
    st.markdown("---")
    st.markdown("<div class='sub-title'>Operations Overview</div>", unsafe_allow_html=True)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.subheader("Inventory Status Overview")
        st.dataframe(st.session_state.db_inventory, use_container_width=True)
    with d_col2:
        st.subheader("Recent Audit Logs")
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)

# --- [3-2. MASTER DATA] ---
elif menu_category == "Master Data":
    st.markdown("<div class='main-title'>Master Data Management</div>", unsafe_allow_html=True)
    sub_tab = st.tabs(["Customers", "Suppliers", "Products", "Warehouses"])
    
    with sub_tab[0]: # Customers
        st.subheader("Customer Master")
        st.dataframe(st.session_state.db_customers[st.session_state.db_customers['is_active']], use_container_width=True)
        with st.expander("Register New Customer"):
            with st.form("new_customer_form"):
                code = st.text_input("Customer Code")
                name = st.text_input("Customer Name")
                currency = st.selectbox("Currency", ["USD", "JPY", "KRW"])
                submitted = st.form_submit_button("Register Customer")
                if submitted and code and name:
                    new_id = len(st.session_state.db_customers) + 1
                    new_row = {"id": new_id, "code": code, "name": name, "currency": currency, "is_active": True}
                    st.session_state.db_customers = pd.concat([st.session_state.db_customers, pd.DataFrame([new_row])], ignore_index=True)
                    log_audit("admin", "Customer", new_id, "CREATE", None, new_row)
                    st.success(f"Customer {name} registered successfully!")
                    st.rerun()

    with sub_tab[1]: # Suppliers
        st.subheader("Supplier Master")
        st.dataframe(st.session_state.db_suppliers[st.session_state.db_suppliers['is_active']], use_container_width=True)

    with sub_tab[2]: # Products
        st.subheader("Product Master")
        st.dataframe(st.session_state.db_products[st.session_state.db_products['is_active']], use_container_width=True)

    with sub_tab[3]: # Warehouses
        st.subheader("Warehouse Master")
        st.dataframe(st.session_state.db_warehouses[st.session_state.db_warehouses['is_active']], use_container_width=True)

# --- [3-3. PURCHASE MANAGEMENT] ---
elif menu_category == "Purchase Management":
    st.markdown("<div class='main-title'>Purchase & Receiving Management</div>", unsafe_allow_html=True)
    p_tab = st.tabs(["Purchase Request", "Purchase Order", "Receiving (입고)"])
    
    with p_tab[1]: # Purchase Order
        st.subheader("Purchase Order Creation")
        st.warning("⚠️ Absolute Rule: Supplier PO Number MUST be entered manually. No auto-generation.")
        
        with st.form("po_form"):
            supplier_id = st.selectbox("Supplier", st.session_state.db_suppliers['id'].tolist(), 
                                       format_func=lambda x: st.session_state.db_suppliers.loc[st.session_state.db_suppliers['id']==x, 'name'].values[0])
            supplier_po_no = st.text_input("Supplier Issued PO Number (Mandatory)", help="Enter exact PO number provided by supplier")
            product_id = st.selectbox("Product", st.session_state.db_products['id'].tolist(),
                                      format_func=lambda x: st.session_state.db_products.loc[st.session_state.db_products['id']==x, 'name'].values[0])
            qty = st.number_input("Quantity", min_value=1, value=100)
            po_submit = st.form_submit_button("Submit Purchase Order")
            
            if po_submit:
                # Unique constraint check: supplier_id + supplier_po_no
                duplicate = any((po['supplier_id'] == supplier_id and po['supplier_po_no'] == supplier_po_no) for po in st.session_state.db_purchase_orders)
                if not supplier_po_no:
                    st.error("Supplier PO Number is mandatory!")
                elif duplicate:
                    st.error("Duplicate Error: This Supplier PO Number already exists for the selected Supplier.")
                else:
                    po_id = len(st.session_state.db_purchase_orders) + 1
                    po_data = {
                        "id": po_id,
                        "supplier_id": supplier_id,
                        "supplier_po_no": supplier_po_no,
                        "product_id": product_id,
                        "quantity": qty,
                        "status": "APPROVED",
                        "order_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.db_purchase_orders.append(po_data)
                    log_audit("admin", "PurchaseOrder", po_id, "CREATE", None, po_data)
                    st.success(f"PO registered successfully: {supplier_po_no}")
                    st.rerun()

        st.subheader("Purchase Orders List")
        st.dataframe(pd.DataFrame(st.session_state.db_purchase_orders), use_container_width=True)

    with p_tab[2]: # Receiving
        st.subheader("Receiving Execution (입고 처리)")
        if not st.session_state.db_purchase_orders:
            st.info("No active Purchase Orders available for receiving.")
        else:
            open_pos = [po for po in st.session_state.db_purchase_orders if po['status'] == 'APPROVED']
            if open_pos:
                selected_po_id = st.selectbox("Select PO to Receive", [po['id'] for po in open_pos],
                                              format_func=lambda x: f"PO: {[po['supplier_po_no'] for po in open_pos if po['id']==x][0]}")
                target_po = next(po for po in open_pos if po['id'] == selected_po_id)
                wh_id = st.selectbox("Destination Warehouse", st.session_state.db_warehouses['id'].tolist(),
                                     format_func=lambda x: st.session_state.db_warehouses.loc[st.session_state.db_warehouses['id']==x, 'name'].values[0])
                
                if st.button("Complete Receiving (COMPLETED)"):
                    # 1. Update PO status
                    target_po['status'] = 'COMPLETED'
                    
                    # 2. Increase Inventory
                    inv_df = st.session_state.db_inventory
                    mask = (inv_df['warehouse_id'] == wh_id) & (inv_df['product_id'] == target_po['product_id'])
                    
                    if mask.any():
                        st.session_state.db_inventory.loc[mask, 'current_stock'] += target_po['quantity']
                    else:
                        new_inv = {"warehouse_id": wh_id, "product_id": target_po['product_id'], "current_stock": target_po['quantity'], "reserved_stock": 0}
                        st.session_state.db_inventory = pd.concat([st.session_state.db_inventory, pd.DataFrame([new_inv])], ignore_index=True)
                        
                    # 3. Record Stock Transaction = INBOUND
                    tx = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "INBOUND",
                        "warehouse_id": wh_id,
                        "product_id": target_po['product_id'],
                        "quantity": target_po['quantity'],
                        "reference_no": target_po['supplier_po_no']
                    }
                    st.session_state.db_stock_transactions.append(tx)
                    log_audit("admin", "Receiving", target_po['id'], "RECEIVE", None, tx)
                    st.success(f"Receiving completed! Stock updated (+{target_po['quantity']}) and Transaction logged.")
                    st.rerun()

# --- [3-4. INVENTORY MANAGEMENT] ---
elif menu_category == "Inventory Management":
    st.markdown("<div class='main-title'>Inventory Management</div>", unsafe_allow_html=True)
    i_tab = st.tabs(["Stock Overview", "Stock Transfer", "Transaction History"])
    
    with i_tab[0]: # Overview
        st.subheader("Current Stock Status")
        st.dataframe(st.session_state.db_inventory, use_container_width=True)
        
    with i_tab[1]: # Stock Transfer
        st.subheader("Warehouse-to-Warehouse Transfer")
        col1, col2 = st.columns(2)
        with col1:
            from_wh = st.selectbox("From Warehouse", st.session_state.db_warehouses['id'].tolist())
        with col2:
            to_wh = st.selectbox("To Warehouse", [w for w in st.session_state.db_warehouses['id'].tolist() if w != from_wh])
            
        prod_id = st.selectbox("Transfer Product", st.session_state.db_products['id'].tolist())
        transfer_qty = st.number_input("Transfer Quantity", min_value=1, value=10)
        
        if st.button("Execute Stock Transfer"):
            inv_df = st.session_state.db_inventory
            from_mask = (inv_df['warehouse_id'] == from_wh) & (inv_df['product_id'] == prod_id)
            
            if not from_mask.any() or inv_df.loc[from_mask, 'current_stock'].values[0] < transfer_qty:
                st.error("Insufficient inventory in origin warehouse!")
            else:
                # Deduct origin
                st.session_state.db_inventory.loc[from_mask, 'current_stock'] -= transfer_qty
                
                # Add destination
                to_mask = (inv_df['warehouse_id'] == to_wh) & (inv_df['product_id'] == prod_id)
                if to_mask.any():
                    st.session_state.db_inventory.loc[to_mask, 'current_stock'] += transfer_qty
                else:
                    new_inv = {"warehouse_id": to_wh, "product_id": prod_id, "current_stock": transfer_qty, "reserved_stock": 0}
                    st.session_state.db_inventory = pd.concat([st.session_state.db_inventory, pd.DataFrame([new_inv])], ignore_index=True)
                    
                # Transaction Log
                tx = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "TRANSFER",
                    "warehouse_id": f"{from_wh} -> {to_wh}",
                    "product_id": prod_id,
                    "quantity": transfer_qty,
                    "reference_no": "INTERNAL-TRANSFER"
                }
                st.session_state.db_stock_transactions.append(tx)
                log_audit("admin", "Inventory", 0, "TRANSFER", None, tx)
                st.success("Stock transfer successfully executed!")
                st.rerun()

    with i_tab[2]: # Transaction History
        st.subheader("All Stock Transactions (Audit Trace)")
        st.dataframe(pd.DataFrame(st.session_state.db_stock_transactions), use_container_width=True)

# --- [3-5. SALES MANAGEMENT] ---
elif menu_category == "Sales Management":
    st.markdown("<div class='main-title'>Sales & Invoice Management</div>", unsafe_allow_html=True)
    s_tab = st.tabs(["Customer Orders", "Delivery (납품)", "Invoice (합산 청구)"])
    
    with s_tab[0]: # Orders
        st.subheader("Customer Order Registration")
        st.warning("⚠️ Absolute Rule: Customer PO Number MUST be entered manually. No auto-generation.")
        
        with st.form("sales_order_form"):
            cust_id = st.selectbox("Customer", st.session_state.db_customers['id'].tolist(),
                                   format_func=lambda x: st.session_state.db_customers.loc[st.session_state.db_customers['id']==x, 'name'].values[0])
            cust_po_no = st.text_input("Customer PO Number (e.g. ABC-PO-202608-001)")
            prod_id = st.selectbox("Product", st.session_state.db_products['id'].tolist(),
                                   format_func=lambda x: st.session_state.db_products.loc[st.session_state.db_products['id']==x, 'name'].values[0])
            order_qty = st.number_input("Order Quantity", min_value=1, value=50)
            so_submit = st.form_submit_button("Create Sales Order")
            
            if so_submit:
                duplicate = any((so['customer_id'] == cust_id and so['customer_po_no'] == cust_po_no) for so in st.session_state.db_sales_orders)
                if not cust_po_no:
                    st.error("Customer PO Number is required!")
                elif duplicate:
                    st.error("Duplicate Customer PO Number detected for this Customer.")
                else:
                    so_id = len(st.session_state.db_sales_orders) + 1
                    unit_p = st.session_state.db_products.loc[st.session_state.db_products['id']==prod_id, 'unit_price'].values[0]
                    so_data = {
                        "id": so_id,
                        "customer_id": cust_id,
                        "customer_po_no": cust_po_no,
                        "product_id": prod_id,
                        "quantity": order_qty,
                        "unit_price": unit_p,
                        "total_amount": order_qty * unit_p,
                        "status": "APPROVED"
                    }
                    st.session_state.db_sales_orders.append(so_data)
                    log_audit("admin", "SalesOrder", so_id, "CREATE", None, so_data)
                    st.success("Sales Order successfully registered!")
                    st.rerun()
                    
        st.dataframe(pd.DataFrame(st.session_state.db_sales_orders), use_container_width=True)

    with s_tab[1]: # Delivery
        st.subheader("Delivery Execution (Partial / Full Delivery)")
        open_sos = [so for so in st.session_state.db_sales_orders if so['status'] == 'APPROVED']
        if open_sos:
            selected_so_id = st.selectbox("Select Sales Order for Delivery", [so['id'] for so in open_sos],
                                          format_func=lambda x: f"SO: {[so['customer_po_no'] for so in open_sos if so['id']==x][0]}")
            target_so = next(so for so in open_sos if so['id'] == selected_so_id)
            
            wh_id = st.selectbox("Dispatch Warehouse", st.session_state.db_warehouses['id'].tolist())
            deliv_qty = st.number_input("Delivery Quantity", min_value=1, max_value=target_so['quantity'], value=target_so['quantity'])
            
            # Transaction Type according to Rules
            trans_type = st.selectbox("Delivery Type", ["NORMAL", "FOC", "SAMPLE"], help="FOC & SAMPLE: Kept in delivery records, excluded from billing amount.")
            shipping_type = st.radio("Shipping Fee Option", ["FREE", "PAID"])
            shipping_fee = st.number_input("Shipping Fee Amount", min_value=0, value=0 if shipping_type == "FREE" else 5000)
            
            if st.button("Complete Delivery (COMPLETED)"):
                # Inventory Deduction Check
                inv_df = st.session_state.db_inventory
                mask = (inv_df['warehouse_id'] == wh_id) & (inv_df['product_id'] == target_so['product_id'])
                
                if not mask.any() or inv_df.loc[mask, 'current_stock'].values[0] < deliv_qty:
                    st.error("Insufficient warehouse stock to complete delivery!")
                else:
                    # 1. Deduct Inventory
                    st.session_state.db_inventory.loc[mask, 'current_stock'] -= deliv_qty
                    
                    # 2. Record Transaction = OUTBOUND
                    tx = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "OUTBOUND",
                        "warehouse_id": wh_id,
                        "product_id": target_so['product_id'],
                        "quantity": deliv_qty,
                        "reference_no": target_so['customer_po_no']
                    }
                    st.session_state.db_stock_transactions.append(tx)
                    
                    # 3. Record Delivery
                    deliv_id = len(st.session_state.db_deliveries) + 1
                    deliv_data = {
                        "id": deliv_id,
                        "order_id": target_so['id'],
                        "customer_id": target_so['customer_id'],
                        "product_id": target_so['product_id'],
                        "quantity": deliv_qty,
                        "unit_price": target_so['unit_price'],
                        "trans_type": trans_type,
                        "shipping_fee": shipping_fee,
                        "billed": False,
                        "delivery_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.db_deliveries.append(deliv_data)
                    log_audit("admin", "Delivery", deliv_id, "COMPLETE", None, deliv_data)
                    st.success("Delivery completed and stock updated (-OUTBOUND)!")
                    st.rerun()
                    
        st.subheader("Delivery Records")
        st.dataframe(pd.DataFrame(st.session_state.db_deliveries), use_container_width=True)

    with s_tab[2]: # Monthly Invoice Aggregation
        st.subheader("Monthly Invoice Aggregation & Issuance")
        st.info("Rule: Consolidate multiple deliveries in a month into a single Invoice. Exclude FOC/SAMPLE from merchandise charges.")
        
        unbilled_deliveries = [d for d in st.session_state.db_deliveries if not d['billed']]
        if unbilled_deliveries:
            df_unbilled = pd.DataFrame(unbilled_deliveries)
            st.write("Unbilled Deliveries:")
            st.dataframe(df_unbilled, use_container_width=True)
            
            target_cust = st.selectbox("Select Customer to Issue Invoice", df_unbilled['customer_id'].unique())
            
            if st.button("Generate Monthly Combined Invoice"):
                cust_delivs = [d for d in unbilled_deliveries if d['customer_id'] == target_cust]
                
                total_merchandise = 0
                total_shipping = 0
                
                for d in cust_delivs:
                    # NORMAL charges merchandise, FOC/SAMPLE excludes merchandise
                    if d['trans_type'] == 'NORMAL':
                        total_merchandise += (d['quantity'] * d['unit_price'])
                    total_shipping += d['shipping_fee']
                    d['billed'] = True # Mark as billed
                    
                final_invoice_amount = total_merchandise + total_shipping
                inv_id = len(st.session_state.db_invoices) + 1
                inv_data = {
                    "id": inv_id,
                    "customer_id": target_cust,
                    "merchandise_amount": total_merchandise,
                    "shipping_amount": total_shipping,
                    "total_amount": final_invoice_amount,
                    "status": "ISSUED",
                    "issue_date": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.db_invoices.append(inv_data)
                log_audit("admin", "Invoice", inv_id, "CREATE", None, inv_data)
                st.success(f"Invoice #{inv_id} created for Total: {final_invoice_amount:,.0f} (Merchandise: {total_merchandise:,.0f}, Shipping: {total_shipping:,.0f})")
                st.rerun()
                
        st.subheader("Issued Invoices History")
        st.dataframe(pd.DataFrame(st.session_state.db_invoices), use_container_width=True)

# --- [3-6. EC MANAGEMENT] ---
elif menu_category == "EC Management":
    st.markdown("<div class='main-title'>EC Sales Management (Manual Input)</div>", unsafe_allow_html=True)
    st.caption("Note: EC sales are tracked manually for reporting and separate from B2B Customer Orders.")
    
    with st.form("ec_sales_form"):
        platform = st.selectbox("EC Platform", ["Qoo10", "Rakuten", "Amazon JP", "TikTok Shop"])
        account = st.text_input("Account Name", value="Official Store A")
        sale_date = st.date_input("Sale Date")
        amount = st.number_input("Sales Amount", min_value=0, value=15000)
        currency = st.selectbox("Currency", ["JPY", "USD", "KRW"])
        ec_submit = st.form_submit_button("Record EC Sale")
        
        if ec_submit:
            ec_id = len(st.session_state.db_ec_sales) + 1
            ec_data = {
                "id": ec_id,
                "platform": platform,
                "account": account,
                "sale_date": str(sale_date),
                "amount": amount,
                "currency": currency
            }
            st.session_state.db_ec_sales.append(ec_data)
            log_audit("admin", "EC_Sales", ec_id, "CREATE", None, ec_data)
            st.success("EC Sales record saved!")
            st.rerun()
            
    st.dataframe(pd.DataFrame(st.session_state.db_ec_sales), use_container_width=True)

# --- [3-7. SETTLEMENT] ---
elif menu_category == "Settlement":
    st.markdown("<div class='main-title'>Settlement & Receivables</div>", unsafe_allow_html=True)
    st.subheader("Invoice Payment Status")
    
    if st.session_state.db_invoices:
        inv_df = pd.DataFrame(st.session_state.db_invoices)
        st.dataframe(inv_df, use_container_width=True)
        
        open_invoices = [i for i in st.session_state.db_invoices if i['status'] == 'ISSUED']
        if open_invoices:
            inv_to_pay = st.selectbox("Select Invoice to Settle", [i['id'] for i in open_invoices])
            if st.button("Mark Invoice as PAID"):
                target = next(i for i in st.session_state.db_invoices if i['id'] == inv_to_pay)
                target['status'] = 'PAID'
                log_audit("admin", "Settlement", target['id'], "UPDATE", {"status": "ISSUED"}, {"status": "PAID"})
                st.success(f"Invoice #{inv_to_pay} marked as PAID.")
                st.rerun()
    else:
        st.info("No active invoices for settlement.")

# --- [3-8. SYSTEM ADMINISTRATION] ---
elif menu_category == "System Administration":
    st.markdown("<div class='main-title'>System Administration & Audit Logs</div>", unsafe_allow_html=True)
    sys_tab = st.tabs(["Users & Roles", "Audit Logs", "Attachments"])
    
    with sys_tab[0]:
        st.subheader("User Role Permissions Matrix")
        st.markdown("""
        - **ADMIN**: Full access (Create, Read, Update, Delete, Approve, Settings)
        - **MANAGER**: Operational Management & Approvals
        - **USER**: Standard Data Entry & Daily Reporting
        - **VIEWER**: Read-only Access across all modules
        """)
        
    with sys_tab[1]:
        st.subheader("System Global Audit Logs")
        st.caption("Tracks all CREATE, UPDATE, DELETE, COMPLETE, and RECEIVE events across the ERP.")
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
        
    with sys_tab[2]:
        st.subheader("Supabase Storage Attachments")
        st.file_uploader("Upload ERP Document (PO, Invoice, Contract)", type=['pdf', 'png', 'xlsx'])
