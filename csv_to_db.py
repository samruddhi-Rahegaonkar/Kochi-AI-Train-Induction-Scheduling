import pandas as pd
from database_setup import create_table, create_connection, fetch_all

def insert_from_csv(csv_file):
    """Insert multiple rows from a CSV file into the trains table.

    Works with both file paths (str) and file-like objects (Streamlit uploads).
    """
    # ✅ Reset file pointer if it's a file-like object
    if hasattr(csv_file, "seek"):
        csv_file.seek(0)

    # Load CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Ensure expected columns exist
    expected_cols = [
        "fitness_certificate",
        "job_card",
        "branding_priority",
        "mileage_balancing",
        "cleaning_slot",
        "depot_positioning"
    ]
    if not all(col in df.columns for col in expected_cols):
        raise ValueError(f"CSV must contain columns: {expected_cols}")

    # Save into SQLite
    conn = create_connection()
    df.to_sql("trains", conn, if_exists="append", index=False)
    conn.close()
    print("✅ CSV data inserted into database!")


if __name__ == "__main__":
    # Step 1: Ensure table exists
    create_table()

    # Step 2: Insert from CSV (local file path)
    insert_from_csv("trains.csv")

    # Step 3: Fetch and show records
    data = fetch_all()
    print("📄 Records in DB:")
    for row in data:
        print(row)
