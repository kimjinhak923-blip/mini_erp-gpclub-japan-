import sqlite3
import pandas as pd

DB_FILE = "app_data.db"


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_db():
    """모든 데이터 테이블 초기화"""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 거래처 마스터
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS master_clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_code TEXT UNIQUE,
            client_name TEXT NOT NULL,
            client_type TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            note TEXT
        )
    """
    )

    # 2. 거래처별 등록 제품
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS client_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            box_jan_code TEXT,
            product_name TEXT,
            custom_price REAL,
            note TEXT
        )
    """
    )

    # 3. 상품 마스터
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS master_products (
            box_jan_code TEXT PRIMARY KEY,
            single_jan_code TEXT,
            product_name TEXT,
            category TEXT,
            capacity TEXT,
            cost_price_krw REAL,
            list_price_jpy_excl_tax REAL,
            units_per_box INTEGER,
            single_box_dim TEXT,
            outer_box_dim TEXT
        )
    """
    )

    # 4. 집기 마스터
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS master_fixtures (
            fixture_name TEXT PRIMARY KEY,
            total_qty INTEGER,
            warehouse TEXT,
            total_cost REAL,
            unit_cost REAL
        )
    """
    )

    # 5. 입출고 및 재고 이동 로그 (전체 입출고 등록 내역)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stock_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,            -- 입고 / 출고 / 이동 등
            item_category TEXT,   -- 상품 / 집기
            client_name TEXT,     -- 거래처명
            product_name TEXT,
            warehouse TEXT,
            qty INTEGER,
            unit_price REAL,
            total_amount REAL,
            note TEXT
        )
    """
    )

    # 6. 창고 마스터
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS master_warehouses (
            warehouse_name TEXT PRIMARY KEY,
            location TEXT,
            manager TEXT
        )
    """
    )

    conn.commit()
    conn.close()


# =============================================================================
# 거래처 (Clients) 함수
# =============================================================================
def load_clients():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM master_clients", conn)
    conn.close()
    return df.to_dict("records")


def save_clients(client_list):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM master_clients")
    for c in client_list:
        cursor.execute(
            """
            INSERT INTO master_clients (client_code, client_name, client_type, contact_person, phone, email, address, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                c.get("client_code", ""),
                c.get("client_name", ""),
                c.get("client_type", "매장"),
                c.get("contact_person", ""),
                c.get("phone", ""),
                c.get("email", ""),
                c.get("address", ""),
                c.get("note", ""),
            ),
        )
    conn.commit()
    conn.close()


# =============================================================================
# 거래처별 등록 제품 (Client Products) 함수
# =============================================================================
def load_client_products(client_name=None):
    conn = get_connection()
    if client_name:
        df = pd.read_sql(
            "SELECT * FROM client_products WHERE client_name = ?",
            conn,
            params=(client_name,),
        )
    else:
        df = pd.read_sql("SELECT * FROM client_products", conn)
    conn.close()
    return df.to_dict("records")


def save_client_products(client_product_list):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM client_products")
    for cp in client_product_list:
        cursor.execute(
            """
            INSERT INTO client_products (client_name, box_jan_code, product_name, custom_price, note)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                cp.get("client_name", ""),
                cp.get("box_jan_code", ""),
                cp.get("product_name", ""),
                cp.get("custom_price", 0),
                cp.get("note", ""),
            ),
        )
    conn.commit()
    conn.close()


# =============================================================================
# 상품 (Products) 함수
# =============================================================================
def load_products():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM master_products", conn)
    conn.close()
    return df.to_dict("records")


def save_products(products_list):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM master_products")
    for p in products_list:
        cursor.execute(
            """
            INSERT INTO master_products (
                box_jan_code, single_jan_code, product_name, category,
                capacity, cost_price_krw, list_price_jpy_excl_tax,
                units_per_box, single_box_dim, outer_box_dim
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                p.get("box_jan_code", ""),
                p.get("single_jan_code", "-"),
                p.get("product_name", ""),
                p.get("category", ""),
                p.get("capacity", ""),
                p.get("cost_price_krw", 0),
                p.get("list_price_jpy_excl_tax", 0),
                p.get("units_per_box", 1),
                p.get("single_box_dim", "-"),
                p.get("outer_box_dim", "-"),
            ),
        )
    conn.commit()
    conn.close()


# =============================================================================
# 집기 (Fixtures) 함수
# =============================================================================
def load_fixtures():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM master_fixtures", conn)
    conn.close()
    return df.to_dict("records")


def save_fixtures(fixtures_list):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM master_fixtures")
    for f in fixtures_list:
        cursor.execute(
            """
            INSERT INTO master_fixtures (fixture_name, total_qty, warehouse, total_cost, unit_cost)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                f.get("fixture_name", ""),
                f.get("total_qty", 0),
                f.get("warehouse", ""),
                f.get("total_cost", 0),
                f.get("unit_cost", 0),
            ),
        )
    conn.commit()
    conn.close()


# =============================================================================
# 입출고 로그 및 재고 현황 (Stock Logs & Stock Inventory) 함수
# =============================================================================
def load_stock_logs():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stock_logs ORDER BY id DESC", conn)
    conn.close()
    return df.to_dict("records")


def add_stock_log(
    date,
    log_type,
    item_category,
    product_name,
    warehouse,
    qty,
    client_name="",
    unit_price=0,
    total_amount=0,
    note="",
):
    """입출고 내역 단건 등록"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO stock_logs (date, type, item_category, client_name, product_name, warehouse, qty, unit_price, total_amount, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            date,
            log_type,
            item_category,
            client_name,
            product_name,
            warehouse,
            qty,
            unit_price,
            total_amount,
            note,
        ),
    )
    conn.commit()
    conn.close()


def save_stock_logs_bulk(logs_list):
    """입출고 내역 전체 저장/수정"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stock_logs")
    for l in logs_list:
        cursor.execute(
            """
            INSERT INTO stock_logs (date, type, item_category, client_name, product_name, warehouse, qty, unit_price, total_amount, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                l.get("date", ""),
                l.get("type", "입고"),
                l.get("item_category", "상품"),
                l.get("client_name", ""),
                l.get("product_name", ""),
                l.get("warehouse", ""),
                l.get("qty", 0),
                l.get("unit_price", 0),
                l.get("total_amount", 0),
                l.get("note", ""),
            ),
        )
    conn.commit()
    conn.close()


def get_current_stock():
    """입출고 로그 기반 실시간 상품별/창고별 현재 재고 계산"""
    logs = load_stock_logs()
    if not logs:
        return []

    df = pd.DataFrame(logs)

    # 입고는 (+), 출고는 (-)로 계산
    df["signed_qty"] = df.apply(
        lambda r: r["qty"] if r["type"] == "입고" else -r["qty"], axis=1
    )

    stock_summary = (
        df.groupby(["warehouse", "product_name", "item_category"])[
            "signed_qty"
        ]
        .sum()
        .reset_index()
    )
    stock_summary.rename(columns={"signed_qty": "current_stock"}, inplace=True)
    return stock_summary.to_dict("records")


# =============================================================================
# 창고 (Warehouses) 함수
# =============================================================================
def load_warehouses():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM master_warehouses", conn)
    conn.close()
    if df.empty:
        default_whs = ["SAGAWA", "L&K", "大吉商事"]
        save_warehouses(
            [
                {"warehouse_name": w, "location": "-", "manager": "-"}
                for w in default_whs
            ]
        )
        return [
            {"warehouse_name": w, "location": "-", "manager": "-"}
            for w in default_whs
        ]
    return df.to_dict("records")


def save_warehouses(wh_list):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM master_warehouses")
    for w in wh_list:
        cursor.execute(
            """
            INSERT INTO master_warehouses (warehouse_name, location, manager)
            VALUES (?, ?, ?)
        """,
            (
                w.get("warehouse_name", ""),
                w.get("location", "-"),
                w.get("manager", "-"),
            ),
        )
    conn.commit()
    conn.close()

# db.py 내부 init_db() 함수 안에 추가
def init_db():
    conn = get_connection() # 기존 DB 연결 함수 사용
    cursor = conn.cursor()
    
    # ... 기존 테이블 생성 코드들 ...

    # 🟢 거래처별 공급가 테이블 생성 추가
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_prices (
            client_name TEXT,
            jan_code TEXT,
            product_name TEXT,
            capacity TEXT,
            list_price REAL,
            supply_price REAL,
            supply_rate REAL,
            PRIMARY KEY (client_name, jan_code)
        )
    ''')
    
    conn.commit()
    conn.close()

# =============================================================================
# 거래처별 공급가(단가) DB 연동 함수
# =============================================================================
def load_client_prices():
    """DB에서 거래처별 공급가 데이터를 불러와 중첩 디렉터리 구조로 반환"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT client_name, jan_code, product_name, capacity, list_price, supply_price, supply_rate FROM client_prices")
    rows = cursor.fetchall()
    conn.close()

    # { "거래처명": { "JAN코드": { ... } } } 구조 생성
    client_prices = {}
    for r in rows:
        client_name = r[0]
        jan_code = r[1]
        
        if client_name not in client_prices:
            client_prices[client_name] = {}
            
        client_prices[client_name][jan_code] = {
            "jan_code": jan_code,
            "product_name": r[2],
            "capacity": r[3],
            "list_price": r[4],
            "supply_price": r[5],
            "supply_rate": r[6],
        }
        
    return client_prices


def save_client_prices(client_prices_dict):
    """거래처별 공급가 데이터를 DB에 저장 (기존 데이터 초기화 후 재등록)"""
    conn = get_connection()
    cursor = conn.cursor()

    # 기존 데이터 삭제 후 일괄 재등록
    cursor.execute("DELETE FROM client_prices")

    for client_name, items in client_prices_dict.items():
        for jan_code, info in items.items():
            cursor.execute('''
                INSERT INTO client_prices 
                (client_name, jan_code, product_name, capacity, list_price, supply_price, supply_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_name,
                jan_code,
                info.get("product_name", ""),
                info.get("capacity", "-"),
                float(info.get("list_price", 0)),
                float(info.get("supply_price", 0)),
                float(info.get("supply_rate", 0))
            ))

    conn.commit()
    conn.close()
