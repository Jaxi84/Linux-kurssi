#!/usr/bin/env python3
import os
import requests
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

# Ladataan tunnukset .env-tiedostosta
load_dotenv("cred.env")

API_KEY = os.getenv("API_KEY")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

# Sijainnit
locations = {
    "Oulu": {"lat": 65.0121, "lon": 25.4651},
    "Oulunsalo": {"lat": 64.9290, "lon": 25.4110}
}

# Luo tietokanta, jos ei ole olemassa
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD
)
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
conn.commit()
cursor.close()
conn.close()

# Yhdistetään kantaan
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = conn.cursor()

# Pudotetaan vanha taulu ja luodaan uusi oikealla rakenteella
cursor.execute("DROP TABLE IF EXISTS air_quality_data")
cursor.execute("""
CREATE TABLE air_quality_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50),
    time VARCHAR(5),
    aqi INT,
    co FLOAT,
    no2 FLOAT,
    o3 FLOAT,
    pm2_5 FLOAT,
    pm10 FLOAT
)
""")

# Haetaan data ja tallennetaan
for city, coords in locations.items():
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}"
    response = requests.get(url).json()

    if "list" not in response:
        print(f"Virhe API-vastauksessa kaupungille {city}: {response}")
        continue

    data = response["list"][0]
    aqi = data["main"]["aqi"]
    components = data["components"]

    # Kellonaika HH:MM
    current_time = datetime.now().strftime("%H:%M")

    cursor.execute("""
    INSERT INTO air_quality_data (city, time, aqi, co, no2, o3, pm2_5, pm10)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        city,
        current_time,
        aqi,
        components.get("co"),
        components.get("no2"),
        components.get("o3"),
        components.get("pm2_5"),
        components.get("pm10")
    ))

conn.commit()
cursor.close()
conn.close()
print("Ilmanlaadun data päivitetty! Kellonaika tallennettu muodossa HH:MM.")
