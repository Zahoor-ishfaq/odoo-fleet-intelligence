import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'fleet_dev'),
    'user': os.getenv('DB_USER', 'odoo'),
    'password': os.getenv('DB_PASSWORD', 'odoo'),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def query_df(sql, params=None):
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()


def fetch_vehicles():
    return query_df("""
        SELECT id, plate_number, make, model, year, status, odometer
        FROM fleet_vehicle_custom
    """)


def fetch_trips():
    return query_df("""
        SELECT id, vehicle_id, driver_name, origin, destination,
               distance_km, start_time, end_time, revenue, cost, profit
        FROM fleet_trip
    """)


def fetch_fuel_logs():
    return query_df("""
        SELECT id, vehicle_id, date, liters, cost, odometer, price_per_liter
        FROM fleet_fuel_log
        ORDER BY vehicle_id, date
    """)


def fetch_maintenance():
    return query_df("""
        SELECT id, vehicle_id, maintenance_type, date, cost,
               odometer_at_service, next_due_km
        FROM fleet_maintenance_custom
    """)