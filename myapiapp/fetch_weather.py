#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import requests
import mysql.connector
from datetime import datetime

# Lataa cred.env
load_dotenv("cred.env")

API_KEY = os.getenv("API_KEY")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

# Kaupungit
cities = ["Oulu", "Oulunsalo"]

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

# Yhdistä tietokantaan
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50),
    temperature FLOAT,
    description VARCHAR(100),
    timestamp DATETIME
)''')

# Hae ja tallenna data molemmille kaupungeille
for city in cities:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and "main" in data:
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        timestamp = datetime.now()

        cursor.execute('INSERT INTO weather_data (city, temperature, description, timestamp) VALUES (%s, %s, %s, %s)',
                       (city, temp, desc, timestamp))
        print(f"Data tallennettu: {city} {temp}°C {desc}")
    else:
        print(f"Virhe haettaessa dataa kaupungille {city}: {data}")

conn.commit()
cursor.close()
conn.close()
