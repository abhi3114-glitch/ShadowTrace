import sqlite3
import pandas as pd
from datetime import datetime
import threading

class DBManager:
    def __init__(self, db_path="shadowtrace.db"):
        self.db_path = db_path
        self._local = threading.local()
        self.init_db()

    def _get_conn(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def init_db(self):
        # We use a completely new connection for initialization to avoid thread issues
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sensor Logs (High frequency)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                acc_x REAL,
                acc_y REAL,
                acc_z REAL,
                light_level REAL,
                is_moving BOOLEAN
            )
        """)

        # Movement Events (Aggregated)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movement_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                duration_seconds REAL,
                avg_light REAL,
                cluster_id INTEGER
            )
        """)
        
        conn.commit()
        conn.close()

    def log_reading(self, reading):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_logs (timestamp, acc_x, acc_y, acc_z, light_level, is_moving)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            reading.timestamp,
            reading.acc_x, reading.acc_y, reading.acc_z,
            reading.light_level,
            reading.is_moving
        ))
        conn.commit()

    def get_todays_logs(self):
        conn = self._get_conn()
        query = """
            SELECT * FROM sensor_logs 
            WHERE date(timestamp) = date('now', 'localtime')
            ORDER BY timestamp DESC
        """
        return pd.read_sql_query(query, conn)

    def get_hourly_activity(self):
        conn = self._get_conn()
        query = """
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as activity_count
            FROM sensor_logs
            WHERE is_moving = 1 AND date(timestamp) = date('now', 'localtime')
            GROUP BY hour
            ORDER BY hour
        """
        return pd.read_sql_query(query, conn)
