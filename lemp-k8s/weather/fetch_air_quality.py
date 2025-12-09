
#!/usr/bin/env python3
import os
import requests
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

# Lataa ympäristömuuttujat
load_dotenv("cred.env")

API_KEY = os.getenv("API_KEY")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

# Kaupungit ja koordinaatit
locations = {
    "Oulu": {"lat": 65.0121, "lon": 25.4651},
    "Oulunsalo": {"lat": 64.9290, "lon": 25.4110}
}

def ensure_database():
    conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
    conn.commit()
    cur.close()
    conn.close()

def ensure_table_and_time_type(conn):
    cur = conn.cursor()
    # Luo taulu jos ei ole
    cur.execute("""
    CREATE TABLE IF NOT EXISTS air_quality_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        city VARCHAR(50),
        time DATETIME,
        aqi INT,
        co FLOAT,
        no2 FLOAT,
        o3 FLOAT,
        pm2_5 FLOAT,
        pm10 FLOAT
    )
    """)
    conn.commit()

    # Varmista, että 'time' on DATETIME
    cur.execute("""
        SELECT DATA_TYPE FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = 'time'
    """, (MYSQL_DB, 'air_quality_data'))
    row = cur.fetchone()
    if row and row[0].lower() != 'datetime':
        cur.execute("ALTER TABLE air_quality_data MODIFY COLUMN time DATETIME")
        conn.commit()
    cur.close()

def fetch_and_store(conn):
    cur = conn.cursor()
    for city, coords in locations.items():
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}"
        response = requests.get(url).json()

        if "list" not in response or not response["list"]:
            print(f"Virhe API-vastauksessa kaupungille {city}: {response}")
            continue

        data = response["list"][0]
        aqi = data["main"]["aqi"]
        components = data["components"]

        current_time = datetime.now()  # DATETIME-objekti

        cur.execute("""
        INSERT INTO air_quality_data (city, time, aqi, co, no2, o3, pm2_5, pm10)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            city, current_time, aqi,
            components.get("co"), components.get("no2"), components.get("o3"),
            components.get("pm2_5"), components.get("pm10")
        ))
    conn.commit()
    cur.close()

def main():
    ensure_database()
    conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
    ensure_table_and_time_type(conn)
    fetch_and_store(conn)
    conn.close()
    print("Ilmanlaatu tallennettu kantaan (DATETIME).")

if __name__ == "__main__":
    main()
