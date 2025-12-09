
import streamlit as st
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px

# Lataa ympäristömuuttujat
load_dotenv("cred.env")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

# Yhdistä tietokantaan
conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)

# --- Säädata (rajoita 50 viimeisimpään) ---
query_weather = """
SELECT timestamp, temperature, city
FROM weather_data
ORDER BY timestamp DESC
LIMIT 50
"""
df_weather = pd.read_sql(query_weather, conn)
df_weather.rename(columns={"timestamp": "aika", "temperature": "lämpötilaC", "city": "kaupunki"}, inplace=True)

# --- Ilmanlaatu (CO & O3, viimeiset 4h, fallback viimeiset 50) ---
query_air_4h = """
SELECT time, city, aqi, co, o3
FROM air_quality_data
WHERE time >= NOW() - INTERVAL 4 HOUR
ORDER BY time DESC
LIMIT 50
"""
df_air = pd.read_sql(query_air_4h, conn)

fallback_used = False
if df_air.empty:
    query_air_last50 = """
    SELECT time, city, aqi, co, o3
    FROM air_quality_data
    ORDER BY time DESC
    LIMIT 50
    """
    df_air = pd.read_sql(query_air_last50, conn)
    fallback_used = True

conn.close()

# Muotoile aikaleimat (ei tz-konversiota, käytetään palvelimen aikaa)
if not df_weather.empty:
    df_weather["aika"] = pd.to_datetime(df_weather["aika"]).dt.floor("s")
if not df_air.empty:
    df_air["time"] = pd.to_datetime(df_air["time"]).dt.floor("s")

# ---------- UI ----------
st.title("Sää- ja ilmanlaatudata")

# ====== SÄÄDATA ======
st.subheader("Säädata (Oulu ja Oulunsalo, viimeiset 50 mittausta)")
st.dataframe(df_weather, use_container_width=True, height=350)

fig_temp = px.scatter(df_weather, x="aika", y="lämpötilaC", color="kaupunki", title="Lämpötilan vaihtelut")
fig_temp.update_xaxes(title="Aika")
fig_temp.update_yaxes(title="Lämpötila (°C)")
st.plotly_chart(fig_temp, use_container_width=True)

# ====== ILMANLAATU ======
header = "Ilmanlaatu (CO & O3, viimeiset 4h, max 50 riviä)"
if fallback_used:
    header += " — ei 4h dataa, näytetään viimeiset havainnot"
st.subheader(header)

if df_air.empty:
    st.warning("Ilmanlaatudataa ei löytynyt.")
else:
    # Kaupunkisuodatin
    cities = df_air["city"].unique().tolist()
    selected_cities = st.multiselect("Valitse kaupungit vertailuun", options=cities, default=cities)
    df_filtered = df_air[df_air["city"].isin(selected_cities)].copy()

    # Taulukko
    air_table = df_filtered[["time", "city", "co", "o3"]].rename(columns={"time": "aika", "city": "kaupunki", "co": "CO", "o3": "O3"})
    st.dataframe(air_table, use_container_width=True, height=350)

    # Keskiarvot ja prosenttivertailu
    agg = df_filtered.groupby("city").agg(co_mean=("co", "mean"), o3_mean=("o3", "mean")).reset_index().round(2)

    if len(agg) > 1:
        base_city = agg.iloc[0]
        agg["CO_diff_%"] = ((agg["co_mean"] - base_city["co_mean"]) / base_city["co_mean"] * 100).round(2)
        agg["O3_diff_%"] = ((agg["o3_mean"] - base_city["o3_mean"]) / base_city["o3_mean"] * 100).round(2)
    else:
        agg["CO_diff_%"] = 0
        agg["O3_diff_%"] = 0

    st.markdown("**Kaupunkien vertailutaulukko (CO & O3, keskiarvot ja prosenttierot)**")
    st.dataframe(agg, use_container_width=True)

    # Vertailupylväät
    df_bar = agg.melt(id_vars=["city"], value_vars=["co_mean", "o3_mean"], var_name="Komponentti", value_name="Keskiarvo")
    df_bar["Komponentti"] = df_bar["Komponentti"].replace({"co_mean": "CO (keskiarvo)", "o3_mean": "O3 (keskiarvo)"})

    fig_comp_compare = px.bar(df_bar, x="city", y="Keskiarvo", color="Komponentti", barmode="group", title="CO ja O3 keskiarvot kaupungeittain")
    fig_comp_compare.update_xaxes(title="Kaupunki")
    fig_comp_compare.update_yaxes(title="Pitoisuus")
    st.plotly_chart(fig_comp_compare, use_container_width=True)

    # AQI-trendi
    st.subheader("AQI-trendi")
    fig_aqi = px.line(df_filtered, x="time", y="aqi", color="city", markers=True, title="AQI-trendi (viimeiset havainnot)")
    fig_aqi.update_xaxes(title="Aika", tickformat="%H:%M")
    fig_aqi.update_yaxes(title="AQI")
    st.plotly_chart(fig_aqi, use_container_width=True)
