import sqlite3
import pandas as pd

DB_FILE = "app_data.db"


def get_connection():
    """SQLite DB 커넥션 생성 (타임아웃 10초 설정으로 database locked 예방)"""
    return sqlite3.connect(DB_FILE, timeout=10, check_same_thread=False)


def init_db():
    """모든 데이터 테이블 초기화"""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 거래처 마스터 (통합 테이블)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            client_name TEXT PRIMARY KEY,
            business_type TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            postal_code TEXT,
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

    # 5. 입출고 및 재고 이동 로그
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stock_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,          -- 입고 / 출고 / 이동 등
            item_category TEXT,  -- 상품 / 집기
            client_name TEXT,    -- 거래처명
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

    # 7. 거래처별 전용 단가/공급가 테이블
    cursor.execute(
        """
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
    """
    )

    conn.commit()
    conn.close()


# =============================================================================
# 🏢 거래처 (Clients) 함수 (컬럼 자동 동기화 기능 추가)
# =============================================================================
def _migrate_clients_table(conn):
    """기존 DB 데이터 손실 없이 부족한 컬럼을 자동 추가해주는 스키마 동기화 함수"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            client_name TEXT PRIMARY KEY,
            business_type TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            postal_code TEXT,
            address TEXT,
            note TEXT
        )
    ''')
    
    # 기존 테이블 컬럼 목록 확인
    cursor.execute("PRAGMA table_info(clients)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    
    # 누락된 컬럼 자동 추가 (기존 데이터 보존)
    target_cols = {
        "business_type": "TEXT",
        "contact_person": "TEXT",
        "phone": "TEXT",
        "email": "TEXT",
        "postal_code": "TEXT",
        "address": "TEXT",
        "note": "TEXT"
    }
    
    for col, col_type in target_cols.items():
        if col not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col} {col_type}")
            except Exception:
                pass
    conn.commit()


def load_clients():
    """DB에서 거래처 목록 불러오기"""
    conn = get_connection()
    _migrate_clients_table(conn)  # 테이블 구조 자동 업데이트

    df = pd.read_sql("SELECT * FROM clients", conn)
    conn.close()
    return df.to_dict("records")


def save_clients(clients_list):
    """거래처 목록 저장 (중복 제거 및 안전한 저장)"""
    conn = get_connection()
    _migrate_clients_table(conn)  # 테이블 구조 자동 업데이트
    
    cursor = conn.cursor()

    # 기존 데이터 초기화
    cursor.execute("DELETE FROM clients")

    # 거래처명(client_name) 기준 중복 제거
    unique_clients = {}
    for client in clients_list:
        c_name = client.get("client_name")
        if c_name:
            unique_clients[c_name] = client

    # DB 저장
    for c_name, c in unique_clients.items():
        cursor.execute('''
            INSERT OR REPLACE INTO clients 
            (client_name, business_type, contact_person, phone, email, postal_code, address, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            c_name,
            c.get("business_type", "기타"),
            c.get("contact_person", "-"),
            c.get("phone", "-"),
            c.get("email", "-"),
            c.get("postal_code", "-"),
            c.get("address", "-"),
            c.get("note", "-")
        ))

    conn.commit()
    conn.close()

# =============================================================================
# 🏷️ 거래처별 공급가(Client Prices) 연동 함수
# =============================================================================
def load_client_prices():
    """DB에서 거래처별 공급가 데이터를 불러와 중첩 디렉터리 구조로 반환"""
    conn = get_connection()
    cursor = conn.cursor()

    # 테이블 생성 보장
    cursor.execute(
        """
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
    """
    )

    cursor.execute(
        "SELECT client_name, jan_code, product_name, capacity, list_price, supply_price, supply_rate FROM client_prices"
    )
    rows = cursor.fetchall()
    conn.close()

    # { "거래처명": { "JAN코드": { ... } } } 구조로 파싱
    client_prices = {}
    for r in rows:
        c_name, jan_code = r[0], r[1]
        if c_name not in client_prices:
            client_prices[c_name] = {}

        client_prices[c_name][jan_code] = {
            "jan_code": jan_code,
            "product_name": r[2],
            "capacity": r[3],
            "list_price": r[4],
            "supply_price": r[5],
            "supply_rate": r[6],
        }

    return client_prices


def save_client_prices(client_prices_dict):
    """거래처별 공급가 데이터를 DB에 전체 저장"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
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
    """
    )

    cursor.execute("DELETE FROM client_prices")

    for client_name, items in client_prices_dict.items():
        for jan_code, info in items.items():
            cursor.execute(
                """
                INSERT OR REPLACE INTO client_prices 
                (client_name, jan_code, product_name, capacity, list_price, supply_price, supply_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    client_name,
                    jan_code,
                    info.get("product_name", ""),
                    info.get("capacity", "-"),
                    float(info.get("list_price", 0)),
                    float(info.get("supply_price", 0)),
                    float(info.get("supply_rate", 0)),
                ),
            )

    conn.commit()
    conn.close()


# =============================================================================
# 📦 거래처별 등록 제품 (Client Products) 함수
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
# 🎁 상품 (Products) 함수
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
# 🪑 집기 (Fixtures) 함수
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
# 📊 입출고 로그 및 재고 현황 (Stock Logs & Stock Inventory) 함수
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
# 🏬 창고 (Warehouses) 함수
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
