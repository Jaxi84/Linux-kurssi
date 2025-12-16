import streamlit as st
import mysql.connector
import pandas as pd
import os
import time
import plotly.express as px
from dotenv import load_dotenv

# --- ASETUKSET ---
load_dotenv()

# Haetaan tietokanta-asetukset ympäristömuuttujista
DB_HOST = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST", "db")
DB_USER = os.getenv("MYSQL_USER") or os.getenv("DB_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("MYSQL_DB") or os.getenv("DB_NAME")

# Sivun konfiguraatio
st.set_page_config(
    page_title="Oulun Sääasema",
    page_icon="🌤️",
    layout="wide"
)

# --- APUFUNKTIOT ---

def get_data():
    """Hakee säädatan tietokannasta."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            connect_timeout=5
        )
        # Haetaan viimeisimmät 100 mittausta
        query = """
        SELECT timestamp, temperature, description, city
        FROM weather_data
        WHERE city = 'Oulu'
        ORDER BY timestamp DESC
        LIMIT 100
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

def auto_refresh():
    """Hoitaa sivun automaattisen päivityksen."""
    time.sleep(60) # Odota 60 sekuntia
    try:
        st.rerun() # Uusi komento (uudemmat Streamlit-versiot)
    except AttributeError:
        st.experimental_rerun() # Vanha komento (varmuuden vuoksi)

# --- SIVUN KÄYTTÖLIITTYMÄ (UI) ---

st.title("🌤️ Oulun Sääasema")

# Haetaan data
df_weather, error = get_data()

if error:
    st.error("⚠️ Yhteysvirhe tietokantaan!")
    st.code(error)
    st.info("Yritetään yhdistää uudelleen hetken kuluttua...")
else:
    if df_weather.empty:
        st.warning("Tietokannassa ei ole vielä dataa. Odota hetki, hakija käynnistyy...")
    else:
        # Muotoillaan dataa
        df_weather.rename(columns={"timestamp": "Aika", "temperature": "Lämpötila", "description": "Kuvaus"}, inplace=True)
        df_weather["Aika"] = pd.to_datetime(df_weather["Aika"])

        # Erotetaan uusin mittaus
        latest = df_weather.iloc[0]
        
        # Näytetään yläosan mittarit (KPI)
        col1, col2, col3 = st.columns(3)
        col1.metric("Lämpötila", f"{latest['Lämpötila']} °C")
        col2.metric("Säätila", latest['Kuvaus'].capitalize())
        col3.metric("Viimeisin mittaus", latest['Aika'].strftime("%H:%M:%S"))

        st.divider()

        # Piirretään kuvaaja
        st.subheader("Lämpötilahistoria (viimeiset 100 mittausta)")
        
        # Luodaan kaunis viivakaavio
        fig = px.line(df_weather, x="Aika", y="Lämpötila", markers=True, title="Lämpötilan kehitys")
        fig.update_traces(line_color='#007bff', line_width=3)
        st.plotly_chart(fig, use_container_width=True)

# --- ALAVIITE & REFRESH ---
st.divider()
st.caption(f"Sivu päivittyy automaattisesti minuutin välein. Serverin aika: {time.strftime('%H:%M:%S')}")

# Käynnistetään automaattinen päivitys
auto_refresh()
