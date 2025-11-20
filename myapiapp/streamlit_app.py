import streamlit as st
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px

# Ladataan cred.env
load_dotenv("cred.env")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

# Yhteys kantaan
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)

# --- Säädata ---
query_oulu = "SELECT timestamp, temperature FROM weather_data WHERE city='Oulu' ORDER BY timestamp DESC LIMIT 50"
df_oulu = pd.read_sql(query_oulu, conn)
df_oulu.rename(columns={"timestamp": "aika", "temperature": "lämpötilaC"}, inplace=True)
df_oulu["kaupunni"] = "Oulu"

query_oulunsalo = "SELECT timestamp, temperature FROM weather_data WHERE city='Oulunsalo' ORDER BY timestamp DESC LIMIT 50"
df_oulunsalo = pd.read_sql(query_oulunsalo, conn)
df_oulunsalo.rename(columns={"timestamp": "aika", "temperature": "lämpötilaC"}, inplace=True)
df_oulunsalo["kaupunni"] = "Oulunsalo"

# --- Ilmanlaatudata ---
query_air = "SELECT timestamp, city, aqi, co, no2, o3, pm2_5, pm10 FROM air_quality_data ORDER BY timestamp DESC LIMIT 50"
df_air = pd.read_sql(query_air, conn)

conn.close()

# Yhdistetään säädata
df_all = pd.concat([df_oulu, df_oulunsalo])

# --- Streamlit UI ---
st.title("Sää- ja ilmanlaatudata")

# Säädata
st.subheader("Säädata (Oulu ja Oulunsalo)")
st.dataframe(df_all)

fig_temp = px.scatter(
    df_all,
    x="aika",
    y="lämpötilaC",
    color="kaupunni",
    title="Lämpötilan vaihtelut",
    labels={"aika": "Aika", "lämpötilaC": "Lämpötila (°C)", "kaupunni": "Kaupunni"},
    hover_data=["kaupunni", "aika", "lämpötilaC"]
)
st.plotly_chart(fig_temp, use_container_width=True)

# Ilmanlaatu
st.subheader("Ilmanlaatu (AQI ja komponentit)")
st.dataframe(df_air)

fig_aqi = px.line(
    df_air,
    x="timestamp",
    y="aqi",
    color="city",
    title="AQI-trendi",
    labels={"timestamp": "Aika", "aqi": "Ilmanlaatuindeksi (AQI)", "city": "Kaupunki"}
)
st.plotly_chart(fig_aqi, use_container_width=True)

# Voit myös tehdä komponenttien jakauman
fig_components = px.bar(
    df_air,
    x="timestamp",
    y=["co", "no2", "o3", "pm2_5", "pm10"],
    title="Ilmanlaadun komponentit",
    labels={"value": "Pitoisuus", "variable": "Komponentti"},
    barmode="group"
)
st.plotly_chart(fig_components, use_container_width=True)
