import sqlite3

DB_NAME= "trains.db"

def create_connection(db_name=DB_NAME):
    """Create SQLite connection (creates file if not exists)."""
    connection = sqlite3.connect(db_name)
    return connection

def create_table():
    """Create the trains table with all required fields."""
    connection=create_connection()
    cursor=connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fitness_certificate TEXT,
        job_card TEXT,
        branding_priority TEXT,
        mileage_balancing REAL,
        cleaning_slot TEXT,
        depot_positioning TEXT
    )
    """)

    connection.commit()
    connection.close()
    print("Table 'trains' created successfully!")


def insert_train(fitness_certificate, job_card, branding_priority, mileage_balancing, cleaning_slot, depot_positioning ):
    connection=create_connection()
    cursor=connection.cursor()

    cursor.execute("""
    INSERT INTO trains 
    (fitness_certificate, job_card, branding_priority, mileage_balancing, cleaning_slot, depot_positioning)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (fitness_certificate, job_card, branding_priority,
          mileage_balancing, cleaning_slot, depot_positioning))
    
    connection.commit()
    connection.close()
    print("Record Inserted")
    
def fetch_all():
    connection=create_connection()
    cursor=connection.cursor()

    cursor.execute("SELECT * FROM trains")
    rows=cursor.fetchall()

    connection.close()
    return rows


if __name__ == "__main__":
    create_table()

    insert_train("Valid till 2026", "JC-12345", "High", 12000.5, "Slot-A", "Depot-1")
    insert_train("Expired", "JC-54321", "Medium", 8000.0, "Slot-B", "Depot-2")

    data = fetch_all()
    print("📄 All Records:")
    for row in data:
        print(row)

