"""
Database module for Restaurant ERP System
Uses SQLite for local storage - no external DB server needed
"""
import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restaurant_erp.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Users ──────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            full_name   TEXT    NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'cashier',  -- admin | manager | cashier
            is_active   INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Categories ─────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            color       TEXT    NOT NULL DEFAULT '#4A90D9',
            icon        TEXT    NOT NULL DEFAULT '🍽️',
            sort_order  INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── Menu Items ─────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id  INTEGER NOT NULL REFERENCES categories(id),
            name         TEXT    NOT NULL,
            description  TEXT,
            price        REAL    NOT NULL,
            cost         REAL    NOT NULL DEFAULT 0,
            image_path   TEXT,
            is_available INTEGER NOT NULL DEFAULT 1,
            tax_rate     REAL    NOT NULL DEFAULT 0.14,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Tables ─────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_tables (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            number      TEXT    NOT NULL UNIQUE,
            capacity    INTEGER NOT NULL DEFAULT 4,
            status      TEXT    NOT NULL DEFAULT 'free'  -- free | occupied | reserved
        )
    """)

    # ── Orders ─────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number    TEXT    NOT NULL UNIQUE,
            table_id        INTEGER REFERENCES restaurant_tables(id),
            order_type      TEXT    NOT NULL DEFAULT 'dine_in',  -- dine_in | takeaway | delivery
            customer_name   TEXT,
            customer_phone  TEXT,
            status          TEXT    NOT NULL DEFAULT 'open',  -- open | completed | cancelled | refunded
            user_id         INTEGER NOT NULL REFERENCES users(id),
            subtotal        REAL    NOT NULL DEFAULT 0,
            discount        REAL    NOT NULL DEFAULT 0,
            discount_type   TEXT    NOT NULL DEFAULT 'amount',  -- amount | percent
            tax_amount      REAL    NOT NULL DEFAULT 0,
            total           REAL    NOT NULL DEFAULT 0,
            payment_method  TEXT,   -- cash | card | wallet
            amount_paid     REAL    NOT NULL DEFAULT 0,
            change_due      REAL    NOT NULL DEFAULT 0,
            notes           TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            completed_at    TEXT
        )
    """)

    # ── Order Items ────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id     INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            menu_item_id INTEGER NOT NULL REFERENCES menu_items(id),
            item_name    TEXT    NOT NULL,
            quantity     INTEGER NOT NULL DEFAULT 1,
            unit_price   REAL    NOT NULL,
            tax_rate     REAL    NOT NULL DEFAULT 0.14,
            notes        TEXT
        )
    """)

    # ── Expenses ───────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            date        TEXT    NOT NULL DEFAULT (date('now')),
            user_id     INTEGER NOT NULL REFERENCES users(id),
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Inventory ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL UNIQUE,
            unit          TEXT    NOT NULL DEFAULT 'كيلو',
            quantity      REAL    NOT NULL DEFAULT 0,
            min_quantity  REAL    NOT NULL DEFAULT 0,
            cost_per_unit REAL    NOT NULL DEFAULT 0,
            category      TEXT    NOT NULL DEFAULT 'عام',
            updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Inventory Transactions ─────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER NOT NULL REFERENCES inventory(id),
            type         TEXT    NOT NULL,  -- in | out | adjustment
            quantity     REAL    NOT NULL,
            unit_cost    REAL    NOT NULL DEFAULT 0,
            notes        TEXT,
            user_id      INTEGER NOT NULL REFERENCES users(id),
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Shift / Cash Register Sessions ────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id),
            opening_cash    REAL    NOT NULL DEFAULT 0,
            closing_cash    REAL,
            total_sales     REAL    NOT NULL DEFAULT 0,
            total_orders    INTEGER NOT NULL DEFAULT 0,
            status          TEXT    NOT NULL DEFAULT 'open',  -- open | closed
            opened_at       TEXT    NOT NULL DEFAULT (datetime('now')),
            closed_at       TEXT
        )
    """)

    # ── Delivery Orders ───────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id        INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            delivery_person TEXT    NOT NULL,
            driver_phone    TEXT,
            delivery_address TEXT   NOT NULL,
            delivery_notes  TEXT,
            delivery_fee    REAL    NOT NULL DEFAULT 0,
            status          TEXT    NOT NULL DEFAULT 'pending',  -- pending | assigned | in_transit | delivered | cancelled
            assigned_at     TEXT,
            started_at      TEXT,
            delivered_at    TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.commit()

    # ── Seed Default Data ──────────────────────────────────────────────────────
    _seed_defaults(conn)
    conn.close()


def _seed_defaults(conn):
    cur = conn.cursor()

    # Admin user
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("admin", hash_password("admin123"), "المدير العام", "admin"))

        cur.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("cashier1", hash_password("1234"), "كاشير الوردية الصباحية", "cashier"))

    # Default categories
    cur.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] == 0:
        cats = [
            ("المشويات", "#E74C3C", "🔥", 1),
            ("الأسماك", "#3498DB", "🐟", 2),
            ("السلطات", "#27AE60", "🥗", 3),
            ("الأطباق الجانبية", "#F39C12", "🍟", 4),
            ("المشروبات الساخنة", "#8E44AD", "☕", 5),
            ("المشروبات الباردة", "#16A085", "🥤", 6),
            ("الحلويات", "#E98B2A", "🍰", 7),
            ("وجبات الأطفال", "#E91E8C", "🧒", 8),
        ]
        cur.executemany(
            "INSERT INTO categories (name, color, icon, sort_order) VALUES (?,?,?,?)", cats
        )

    # Default menu items
    cur.execute("SELECT COUNT(*) FROM menu_items")
    if cur.fetchone()[0] == 0:
        items = [
            (1, "كباب مشكل", "تشكيلة من الكباب المشوي مع الخبز والسلطة", 85.0, 35.0, 0.14),
            (1, "شيش طاووق", "دجاج مشوي بالتتبيلة السرية", 75.0, 28.0, 0.14),
            (1, "كفتة مشوية", "لحم مفروم بالبهارات على الفحم", 70.0, 25.0, 0.14),
            (1, "ستيك لحم", "ستيك لحم بقري بالصلصة والخضار", 120.0, 55.0, 0.14),
            (2, "سمك فيليه", "فيليه سمك مقلي مع البطاطس", 95.0, 42.0, 0.14),
            (2, "جمبري بالثوم", "جمبري بصلصة الثوم والزبدة", 110.0, 50.0, 0.14),
            (3, "سلطة خضراء", "سلطة طازجة متنوعة", 25.0, 8.0, 0.14),
            (3, "تبولة", "سلطة البقدونس والبرغل", 30.0, 10.0, 0.14),
            (4, "بطاطس مقلية", "بطاطس مقلية مقرمشة", 20.0, 6.0, 0.14),
            (4, "أرز بالخلطة", "أرز بالبهارات والمكسرات", 15.0, 5.0, 0.14),
            (5, "قهوة عربية", "قهوة عربية أصيلة بالهيل", 15.0, 4.0, 0.00),
            (5, "شاي بالنعناع", "شاي طازج بالنعناع", 10.0, 2.0, 0.00),
            (5, "كابتشينو", "قهوة إيطالية مع الحليب المبخر", 25.0, 8.0, 0.00),
            (6, "عصير برتقال طازج", "عصير برتقال طبيعي", 30.0, 10.0, 0.00),
            (6, "ليمون بالنعناع", "عصير ليمون منعش", 25.0, 8.0, 0.00),
            (6, "مياه معدنية", "زجاجة مياه معدنية", 5.0, 1.5, 0.00),
            (7, "كنافة بالجبن", "كنافة طازجة بالجبن والقطر", 35.0, 12.0, 0.14),
            (7, "أم علي", "حلوى مصرية تقليدية بالقشدة", 30.0, 10.0, 0.14),
            (8, "وجبة أطفال دجاج", "دجاج مقلي مع بطاطس وعصير", 45.0, 18.0, 0.14),
        ]
        for it in items:
            cur.execute("""
                INSERT INTO menu_items (category_id, name, description, price, cost, tax_rate)
                VALUES (?,?,?,?,?,?)
            """, it)

    # Default tables
    cur.execute("SELECT COUNT(*) FROM restaurant_tables")
    if cur.fetchone()[0] == 0:
        tables = [(f"T{i}", 4) for i in range(1, 13)]
        cur.executemany(
            "INSERT INTO restaurant_tables (number, capacity) VALUES (?,?)", tables
        )

    conn.commit()


# ── Helper Functions ──────────────────────────────────────────────────────────

def authenticate_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM users
        WHERE username=? AND password=? AND is_active=1
    """, (username, hash_password(password)))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def generate_order_number() -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders")
    count = cur.fetchone()[0] + 1
    conn.close()
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{count:04d}"


def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories ORDER BY sort_order, name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_menu_items(category_id=None, available_only=True):
    conn = get_connection()
    cur = conn.cursor()
    q = "SELECT mi.*, c.name as category_name, c.color as cat_color FROM menu_items mi JOIN categories c ON mi.category_id=c.id"
    params = []
    where = []
    if category_id:
        where.append("mi.category_id=?")
        params.append(category_id)
    if available_only:
        where.append("mi.is_available=1")
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY mi.name"
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_all_orders(date_from=None, date_to=None, status=None, limit=200):
    conn = get_connection()
    cur = conn.cursor()
    q = """
        SELECT o.*, u.full_name as cashier_name,
               rt.number as table_number
        FROM orders o
        LEFT JOIN users u ON o.user_id=u.id
        LEFT JOIN restaurant_tables rt ON o.table_id=rt.id
    """
    where, params = [], []
    if date_from:
        where.append("date(o.created_at) >= ?"); params.append(date_from)
    if date_to:
        where.append("date(o.created_at) <= ?"); params.append(date_to)
    if status:
        where.append("o.status=?"); params.append(status)
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY o.created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_order_items(order_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT oi.*, mi.image_path
        FROM order_items oi
        LEFT JOIN menu_items mi ON oi.menu_item_id=mi.id
        WHERE oi.order_id=?
    """, (order_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_order(order_data: dict, items: list) -> int:
    """Insert or update an order and its items. Returns order id."""
    conn = get_connection()
    cur = conn.cursor()
    if order_data.get("id"):
        cur.execute("""
            UPDATE orders SET table_id=?, order_type=?, customer_name=?,
            customer_phone=?, status=?, subtotal=?, discount=?, discount_type=?,
            tax_amount=?, total=?, payment_method=?, amount_paid=?, change_due=?,
            notes=?, completed_at=?
            WHERE id=?
        """, (
            order_data.get("table_id"), order_data.get("order_type"),
            order_data.get("customer_name"), order_data.get("customer_phone"),
            order_data.get("status"), order_data.get("subtotal"),
            order_data.get("discount", 0), order_data.get("discount_type", "amount"),
            order_data.get("tax_amount"), order_data.get("total"),
            order_data.get("payment_method"), order_data.get("amount_paid", 0),
            order_data.get("change_due", 0), order_data.get("notes"),
            order_data.get("completed_at"),
            order_data["id"]
        ))
        order_id = order_data["id"]
        cur.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
    else:
        cur.execute("""
            INSERT INTO orders (order_number, table_id, order_type, customer_name,
            customer_phone, status, user_id, subtotal, discount, discount_type,
            tax_amount, total, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            order_data.get("order_number"), order_data.get("table_id"),
            order_data.get("order_type", "dine_in"), order_data.get("customer_name"),
            order_data.get("customer_phone"), order_data.get("status", "open"),
            order_data["user_id"], order_data.get("subtotal", 0),
            order_data.get("discount", 0), order_data.get("discount_type", "amount"),
            order_data.get("tax_amount", 0), order_data.get("total", 0),
            order_data.get("notes")
        ))
        order_id = cur.lastrowid

    for it in items:
        cur.execute("""
            INSERT INTO order_items (order_id, menu_item_id, item_name, quantity, unit_price, tax_rate, notes)
            VALUES (?,?,?,?,?,?,?)
        """, (order_id, it["menu_item_id"], it["item_name"],
              it["quantity"], it["unit_price"], it.get("tax_rate", 0.14), it.get("notes")))

    conn.commit()
    conn.close()
    return order_id


def get_dashboard_stats(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as revenue
        FROM orders WHERE date(created_at)=? AND status='completed'
    """, (date_str,))
    row = dict(cur.fetchone())

    cur.execute("""
        SELECT COALESCE(SUM(total),0) FROM orders
        WHERE strftime('%Y-%m', created_at)=strftime('%Y-%m', ?) AND status='completed'
    """, (date_str,))
    monthly = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM orders WHERE status='open'
    """)
    open_orders = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM restaurant_tables WHERE status='occupied'
    """)
    occupied_tables = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM restaurant_tables")
    total_tables = cur.fetchone()[0]

    cur.execute("""
        SELECT mi.name, SUM(oi.quantity) as qty
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id=mi.id
        JOIN orders o ON oi.order_id=o.id
        WHERE date(o.created_at)=? AND o.status='completed'
        GROUP BY oi.menu_item_id ORDER BY qty DESC LIMIT 5
    """, (date_str,))
    top_items = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT strftime('%H', created_at) as hour, COUNT(*) as cnt
        FROM orders WHERE date(created_at)=? AND status='completed'
        GROUP BY hour ORDER BY hour
    """, (date_str,))
    hourly = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "today_orders": row["cnt"],
        "today_revenue": row["revenue"],
        "monthly_revenue": monthly,
        "open_orders": open_orders,
        "occupied_tables": occupied_tables,
        "total_tables": total_tables,
        "top_items": top_items,
        "hourly_sales": hourly,
    }


def get_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM restaurant_tables ORDER BY number")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def update_table_status(table_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE restaurant_tables SET status=? WHERE id=?", (status, table_id))
    conn.commit()
    conn.close()


def get_inventory():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory ORDER BY category, name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_inventory_item(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    if data.get("id"):
        cur.execute("""
            UPDATE inventory SET name=?, unit=?, quantity=?, min_quantity=?,
            cost_per_unit=?, category=?, updated_at=datetime('now') WHERE id=?
        """, (data["name"], data["unit"], data["quantity"], data["min_quantity"],
              data["cost_per_unit"], data["category"], data["id"]))
    else:
        cur.execute("""
            INSERT INTO inventory (name, unit, quantity, min_quantity, cost_per_unit, category)
            VALUES (?,?,?,?,?,?)
        """, (data["name"], data["unit"], data["quantity"], data["min_quantity"],
              data["cost_per_unit"], data["category"]))
    conn.commit()
    conn.close()


def get_expenses(date_from=None, date_to=None):
    conn = get_connection()
    cur = conn.cursor()
    q = "SELECT e.*, u.full_name as user_name FROM expenses e JOIN users u ON e.user_id=u.id"
    where, params = [], []
    if date_from:
        where.append("e.date >= ?"); params.append(date_from)
    if date_to:
        where.append("e.date <= ?"); params.append(date_to)
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY e.created_at DESC"
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_expense(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO expenses (category, description, amount, date, user_id)
        VALUES (?,?,?,?,?)
    """, (data["category"], data["description"], data["amount"],
          data.get("date", datetime.now().strftime("%Y-%m-%d")), data["user_id"]))
    conn.commit()
    conn.close()


def get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, role, is_active, created_at FROM users ORDER BY full_name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_user(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    if data.get("id"):
        if data.get("password"):
            cur.execute("""
                UPDATE users SET username=?, password=?, full_name=?, role=?, is_active=? WHERE id=?
            """, (data["username"], hash_password(data["password"]),
                  data["full_name"], data["role"], data["is_active"], data["id"]))
        else:
            cur.execute("""
                UPDATE users SET username=?, full_name=?, role=?, is_active=? WHERE id=?
            """, (data["username"], data["full_name"], data["role"], data["is_active"], data["id"]))
    else:
        cur.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (?,?,?,?)
        """, (data["username"], hash_password(data["password"]),
              data["full_name"], data.get("role", "cashier")))
    conn.commit()
    conn.close()


def save_menu_item(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    if data.get("id"):
        cur.execute("""
            UPDATE menu_items SET category_id=?, name=?, description=?, price=?, cost=?,
            tax_rate=?, is_available=? WHERE id=?
        """, (data["category_id"], data["name"], data.get("description"),
              data["price"], data.get("cost", 0), data.get("tax_rate", 0.14),
              data.get("is_available", 1), data["id"]))
    else:
        cur.execute("""
            INSERT INTO menu_items (category_id, name, description, price, cost, tax_rate, is_available)
            VALUES (?,?,?,?,?,?,?)
        """, (data["category_id"], data["name"], data.get("description"),
              data["price"], data.get("cost", 0), data.get("tax_rate", 0.14),
              data.get("is_available", 1)))
    conn.commit()
    conn.close()


def delete_menu_item(item_id: int):
    conn = get_connection()
    conn.execute("UPDATE menu_items SET is_available=0 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def open_shift(user_id: int, opening_cash: float) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO shifts (user_id, opening_cash) VALUES (?,?)
    """, (user_id, opening_cash))
    shift_id = cur.lastrowid
    conn.commit()
    conn.close()
    return shift_id


def close_shift(shift_id: int, closing_cash: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as cnt, COALESCE(SUM(total), 0) as total_sales
        FROM orders WHERE status='completed'
        AND date(created_at) = date('now')
    """)
    row = dict(cur.fetchone())
    cur.execute("""
        UPDATE shifts SET closing_cash=?, total_sales=?, total_orders=?,
        status='closed', closed_at=datetime('now') WHERE id=?
    """, (closing_cash, row["total_sales"], row["cnt"], shift_id))
    conn.commit()
    conn.close()


def get_report_data(date_from: str, date_to: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) as total_orders,
            COALESCE(SUM(subtotal), 0) as total_subtotal,
            COALESCE(SUM(discount), 0) as total_discount,
            COALESCE(SUM(tax_amount), 0) as total_tax,
            COALESCE(SUM(total), 0) as total_revenue,
            COALESCE(SUM(CASE WHEN payment_method='cash' THEN total ELSE 0 END), 0) as cash_revenue,
            COALESCE(SUM(CASE WHEN payment_method='card' THEN total ELSE 0 END), 0) as card_revenue,
            COALESCE(SUM(CASE WHEN payment_method='wallet' THEN total ELSE 0 END), 0) as wallet_revenue
        FROM orders
        WHERE date(created_at) BETWEEN ? AND ? AND status='completed'
    """, (date_from, date_to))
    summary = dict(cur.fetchone())

    cur.execute("""
        SELECT date(o.created_at) as day, COUNT(*) as cnt,
               COALESCE(SUM(o.total), 0) as revenue
        FROM orders o
        WHERE date(o.created_at) BETWEEN ? AND ? AND o.status='completed'
        GROUP BY day ORDER BY day
    """, (date_from, date_to))
    daily = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT mi.name, c.name as category,
               SUM(oi.quantity) as total_qty,
               SUM(oi.quantity * oi.unit_price) as total_revenue
        FROM order_items oi
        JOIN menu_items mi ON oi.menu_item_id = mi.id
        JOIN categories c ON mi.category_id = c.id
        JOIN orders o ON oi.order_id = o.id
        WHERE date(o.created_at) BETWEEN ? AND ? AND o.status='completed'
        GROUP BY oi.menu_item_id ORDER BY total_qty DESC
    """, (date_from, date_to))
    items = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses WHERE date BETWEEN ? AND ?
        GROUP BY category
    """, (date_from, date_to))
    expenses = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {"summary": summary, "daily": daily, "items": items, "expenses": expenses}


# ── Delivery Functions ─────────────────────────────────────────────────────────

def get_all_deliveries(status=None, date_from=None, date_to=None, limit=200):
    """Get all delivery orders with optional filters."""
    conn = get_connection()
    cur = conn.cursor()
    q = """
        SELECT d.*, o.order_number, o.customer_name, o.customer_phone,
               o.total, o.created_at as order_time
        FROM deliveries d
        JOIN orders o ON d.order_id=o.id
    """
    where, params = [], []
    if status:
        where.append("d.status=?")
        params.append(status)
    if date_from:
        where.append("date(d.created_at) >= ?")
        params.append(date_from)
    if date_to:
        where.append("date(d.created_at) <= ?")
        params.append(date_to)
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY d.created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_delivery(order_id: int, delivery_data: dict) -> int:
    """Create or update a delivery order."""
    conn = get_connection()
    cur = conn.cursor()
    if delivery_data.get("id"):
        cur.execute("""
            UPDATE deliveries SET delivery_person=?, driver_phone=?,
            delivery_address=?, delivery_notes=?, delivery_fee=?, status=?,
            assigned_at=?, started_at=? WHERE id=?
        """, (
            delivery_data["delivery_person"], delivery_data.get("driver_phone"),
            delivery_data["delivery_address"], delivery_data.get("delivery_notes"),
            delivery_data.get("delivery_fee", 0), delivery_data.get("status", "pending"),
            delivery_data.get("assigned_at"), delivery_data.get("started_at"),
            delivery_data["id"]
        ))
        delivery_id = delivery_data["id"]
    else:
        cur.execute("""
            INSERT INTO deliveries (order_id, delivery_person, driver_phone,
            delivery_address, delivery_notes, delivery_fee, status)
            VALUES (?,?,?,?,?,?,?)
        """, (
            order_id, delivery_data["delivery_person"],
            delivery_data.get("driver_phone"), delivery_data["delivery_address"],
            delivery_data.get("delivery_notes"), delivery_data.get("delivery_fee", 0),
            delivery_data.get("status", "pending")
        ))
        delivery_id = cur.lastrowid
    conn.commit()
    conn.close()
    return delivery_id


def update_delivery_status(delivery_id: int, status: str, timestamp_field=None):
    """Update delivery status and set appropriate timestamp."""
    conn = get_connection()
    cur = conn.cursor()
    if timestamp_field:
        cur.execute(f"""
            UPDATE deliveries SET status=?, {timestamp_field}=datetime('now') WHERE id=?
        """, (status, delivery_id))
    else:
        cur.execute("UPDATE deliveries SET status=? WHERE id=?", (status, delivery_id))
    conn.commit()
    conn.close()


def get_delivery_stats(date_str=None):
    """Get delivery statistics."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) as total, SUM(delivery_fee) as fee_total
        FROM deliveries WHERE date(created_at)=?
    """, (date_str,))
    stats = dict(cur.fetchone())

    cur.execute("""
        SELECT status, COUNT(*) as count
        FROM deliveries WHERE date(created_at)=?
        GROUP BY status
    """, (date_str,))
    by_status = {r["status"]: r["count"] for r in [dict(x) for x in cur.fetchall()]}

    conn.close()
    return {"total": stats["total"], "fee_total": stats["fee_total"] or 0, "by_status": by_status}
