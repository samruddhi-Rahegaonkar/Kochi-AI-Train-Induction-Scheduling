import sqlite3

DB_NAME = "trains.db"


def create_connection(db_name=DB_NAME):
    """Create SQLite connection (creates file if not exists)."""
    connection = sqlite3.connect(db_name)
    return connection


def create_tables():
    """Create all required tables for the project."""
    conn = create_connection()
    cursor = conn.cursor()

    # Master train list
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_number TEXT UNIQUE NOT NULL,
        description TEXT
    )
    """)

    # Fitness certificates
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fitness_certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_id INTEGER,
        certificate_status TEXT,
        valid_till DATE,
        issued_by TEXT,
        FOREIGN KEY (train_id) REFERENCES trains(id)
    )
    """)

    # Job cards
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_id INTEGER,
        job_card_no TEXT,
        status TEXT,
        source_system TEXT,
        FOREIGN KEY (train_id) REFERENCES trains(id)
    )
    """)

    # Branding
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS branding_priorities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_id INTEGER,
        priority_level TEXT,
        campaign_name TEXT,
        exposure_hours REAL,
        FOREIGN KEY (train_id) REFERENCES trains(id)
    )
    """)

    # Mileage
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mileage_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_id INTEGER,
        total_km REAL,
        last_updated DATE,
        FOREIGN KEY (train_id) REFERENCES trains(id)
    )
    """)

    # Cleaning
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cleaning_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_id INTEGER,
        slot_name TEXT,
        scheduled_time TEXT,
        status TEXT,
        FOREIGN KEY (train_id) REFERENCES trains(id)
    )
    """)

    # Depot positions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS depot_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_id INTEGER,
        depot_name TEXT,
        position_code TEXT,
        FOREIGN KEY (train_id) REFERENCES trains(id)
    )
    """)

    conn.commit()
    conn.close()


# Insert helpers
def insert_train(train_number, description=""):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO trains (train_number, description) VALUES (?, ?)",
                (train_number, description))
    conn.commit()
    conn.close()


def insert_record(table, data: dict):
    """Generic insert into any table by dict."""
    conn = create_connection()
    cur = conn.cursor()
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql = f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})"
    cur.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()


def fetch_all(table):
    conn = create_connection()
    cur = conn.cursor()
    # Get column names
    cur.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cur.fetchall()]
    # Get data
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    conn.close()
    # Return as list of dicts
    return [dict(zip(columns, row)) for row in rows]
