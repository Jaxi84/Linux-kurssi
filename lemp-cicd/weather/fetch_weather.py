#!/usr/bin/env python3
import os
import time
from datetime import datetime
from urllib.parse import urlencode

import requests
import mysql.connector
from dotenv import load_dotenv

# Lataa .env
if os.path.exists("/app/.env"):
    load_dotenv("/app/.env")
else:
    load_dotenv()

API_KEY = os.getenv("API_KEY")
MYSQL_USER = os.getenv("DB_USER") or os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("DB_HOST", "db")  # Compose-verkossa 'db'
MYSQL_DB = os.getenv("DB_NAME", "weatherdb")

CITIES = [c.strip() for c in os.getenv("CITY_LIST", "Oulu,Oulunsalo").split(",") if c.strip()]

if not API_KEY:
    raise RuntimeError("API_KEY puuttuu .env:stä")

def ensure_database_and_table():
    # Luo tietokanta jos puuttuu
    conn = mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    cur.close()
    conn.close()

    # Luo taulu
    conn = mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB
    )
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            temperature DECIMAL(5,2) NOT NULL,
            description VARCHAR(200),
            timestamp DATETIME NOT NULL,
            INDEX (city),
            INDEX (timestamp)
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()

def fetch_and_store():
    print(f"Yhdistetään tietokantaan: {MYSQL_HOST}...")
    conn = mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB
    )
    cur = conn.cursor()

    for city in CITIES:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        url = f"https://api.openweathermap.org/data/2.5/weather?{urlencode(params)}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
        except Exception as e:
            print(f"[WARN] Pyyntö epäonnistui kaupungille {city}: {e}")
            continue

        if resp.status_code == 200 and "main" in data and "weather" in data:
            temp = float(data["main"]["temp"])
            desc = data["weather"][0].get("description", "")
            ts = datetime.now()

            cur.execute(
                "INSERT INTO weather_data (city, temperature, description, timestamp) VALUES (%s, %s, %s, %s)",
                (city, temp, desc, ts),
            )
            print(f"[OK] Tallennettu: {city} {temp:.1f}°C {desc}")
        else:
            print(f"[WARN] Virhe {city}: status={resp.status_code}, data={data}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    ensure_database_and_table()
    
    # Ikuinen silmukka
    while True:
        fetch_and_store()
        print("Odotetaan 15 minuuttia ennen seuraavaa hakua...")
        time.sleep(900)  # 900 sekuntia = 15 minuuttia
