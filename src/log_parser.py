import pandas as pd
from flask import current_app
from models import db, LogEntry  # Import from models.py, not app.py

def load_logs():
    """
    Load logs from the database and return a pandas DataFrame.
    """
    try:
        with current_app.app_context():  # Ensure queries run inside app context
            df = pd.read_sql(LogEntry.query.distinct().statement, db.engine)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            print(f"loaded {len(df)} logs")

            return df
    except Exception as e:
        print(f"Error loading logs: {e}")
        return None
    
def import_logs_from_csv(file_path):
    """
    Imports logs from a CSV file into the database.
    """
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)

        # Convert the timestamp column to datetime if necessary
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Insert data into the database
        with db.session.begin():
            for _, row in df.iterrows():
                log_entry = LogEntry(
                    ip_address=row['ip_address'],
                    username=row['username'],
                    action=row['action'],
                    timestamp=row['timestamp'],
                    status_code=row['status_code']
                )
                db.session.add(log_entry)

        print(f"Successfully imported {len(df)} log entries.")
    except Exception as e:
        print(f"Error importing logs: {e}")