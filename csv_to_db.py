import pandas as pd
import datetime
from database_setup import create_connection, create_tables, insert_record

def insert_from_df(df, table_name):
    """Insert multiple rows from DataFrame into a specific table."""

    # Define converters for each table
    converters = {
        "trains": {
            "train_number": lambda x: str(x) if not pd.isna(x) else "",
            "description": lambda x: str(x) if not pd.isna(x) else ""
        },
        "fitness_certificates": {
            "train_id": lambda x: int(float(x)) if not pd.isna(x) else None,
            "certificate_status": lambda x: str(x) if not pd.isna(x) else "Valid",
            "valid_till": lambda x: str(pd.to_datetime(x).date()) if not pd.isna(x) else str(datetime.date.today()),
            "issued_by": lambda x: str(x) if not pd.isna(x) else ""
        },
        "job_cards": {
            "train_id": lambda x: int(float(x)) if not pd.isna(x) else None,
            "job_card_no": lambda x: str(x) if not pd.isna(x) else "",
            "status": lambda x: str(x) if not pd.isna(x) else "Open",
            "source_system": lambda x: str(x) if not pd.isna(x) else "Maximo"
        },
        "branding_priorities": {
            "train_id": lambda x: int(float(x)) if not pd.isna(x) else None,
            "priority_level": lambda x: str(x) if not pd.isna(x) else "Medium",
            "campaign_name": lambda x: str(x) if not pd.isna(x) else "",
            "exposure_hours": lambda x: float(x) if not pd.isna(x) else 0.0
        },
        "mileage_records": {
            "train_id": lambda x: int(float(x)) if not pd.isna(x) else None,
            "total_km": lambda x: float(x) if not pd.isna(x) else 0.0,
            "last_updated": lambda x: str(pd.to_datetime(x).date()) if not pd.isna(x) else str(datetime.date.today())
        },
        "cleaning_slots": {
            "train_id": lambda x: int(float(x)) if not pd.isna(x) else None,
            "slot_name": lambda x: str(x) if not pd.isna(x) else "",
            "scheduled_time": lambda x: str(x) if not pd.isna(x) else "",
            "status": lambda x: str(x) if not pd.isna(x) else "Pending"
        },
        "depot_positions": {
            "train_id": lambda x: int(float(x)) if not pd.isna(x) else None,
            "depot_name": lambda x: str(x) if not pd.isna(x) else "",
            "position_code": lambda x: str(x) if not pd.isna(x) else ""
        }
    }

    table_converters = converters.get(table_name, {})
    expected_keys = list(table_converters.keys())

    # Insert each row using insert_record
    for _, row in df.iterrows():
        data = row.to_dict()
        # Normalize keys to lowercase
        data = {k.lower(): v for k, v in data.items()}
        # Map common variations
        key_map = {
            'train id': 'train_id',
            'job card no': 'job_card_no',
            'certificate status': 'certificate_status',
            'valid till': 'valid_till',
            'issued by': 'issued_by',
            'source system': 'source_system',
            'priority level': 'priority_level',
            'campaign name': 'campaign_name',
            'exposure hours': 'exposure_hours',
            'total km': 'total_km',
            'last updated': 'last_updated',
            'slot name': 'slot_name',
            'scheduled time': 'scheduled_time',
            'depot name': 'depot_name',
            'position code': 'position_code'
        }
        data = {key_map.get(k, k): v for k, v in data.items()}
        # Filter to expected keys
        data = {k: v for k, v in data.items() if k in expected_keys}
        # Apply converters
        for k in list(data.keys()):
            if k in table_converters:
                try:
                    data[k] = table_converters[k](data[k])
                except (ValueError, TypeError):
                    # If conversion fails, set to default
                    if k == 'train_id':
                        data[k] = None
                    elif k in ['exposure_hours', 'total_km']:
                        data[k] = 0.0
                    else:
                        data[k] = ""
        if data:
            insert_record(table_name, data)

    print(f"✅ CSV data inserted into {table_name}!")


if __name__ == "__main__":
    create_tables()
    insert_from_df("trains.csv", "trains")
