import streamlit as st
import mysql.connector
import pandas as pd
import os
import plotly.express as px

# Ympäristömuuttujat (K8s)
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_DB = os.getenv("MYSQL_DB", "appdb")

# Yhdistä tietokantaan
def get_connection():
    return mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)

# --- Säädata (viimeiset 12h) ---
try:
    conn = get_connection()
    # Haetaan data weather_log taulusta 12h ajalta
    query_weather = """
    SELECT timestamp, temperature, city
    FROM weather_log
    WHERE timestamp >= NOW() - INTERVAL 12 HOUR
    ORDER BY timestamp DESC
    """
    df_weather = pd.read_sql(query_weather, conn)
    conn.close()

    # Sarakkeiden nimeäminen
    df_weather.rename(columns={"timestamp": "aika", "temperature": "lämpötilaC", "city": "kaupunki"}, inplace=True)

    # Muotoile aikaleimat
    if not df_weather.empty:
        df_weather["aika"] = pd.to_datetime(df_weather["aika"]).dt.floor("s")

except Exception as e:
    st.error(f"Tietokantavirhe: {e}")
    df_weather = pd.DataFrame()

# ---------- UI ----------
st.set_page_config(page_title="Säähistoria", layout="wide")
st.title("Säädata")

# ====== SÄÄDATA ======
st.subheader("Säädata (Oulu, viimeiset 12h)")

if df_weather.empty:
    st.warning("Ei dataa. Käy painamassa 'Get Weather' -nappia etusivulla!")
else:
    # Taulukko
    st.dataframe(df_weather, use_container_width=True, height=350)

    # Diagrammi (12h)
    fig_temp = px.line(df_weather, x="aika", y="lämpötilaC", markers=True, title="Lämpötilan vaihtelut (12h)")
    fig_temp.update_xaxes(title="Aika")
    fig_temp.update_yaxes(title="Lämpötila (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)
