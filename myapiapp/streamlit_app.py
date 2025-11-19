import streamlit as st
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Lataa cred.env
load_dotenv("cred.env")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

# Yhdistä MySQL-tietokantaan
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)

# Oulun data
query_oulu = "SELECT * FROM weather_data WHERE city='Oulu' ORDER BY timestamp DESC LIMIT 50"
df_oulu = pd.read_sql(query_oulu, conn)

# Oulunsalon data
query_oulunsalo = "SELECT * FROM weather_data WHERE city='Oulunsalo' ORDER BY timestamp DESC LIMIT 50"
df_oulunsalo = pd.read_sql(query_oulunsalo, conn)

conn.close()

# Streamlit UI
st.title("Säädata")
st.subheader("Oulu")
st.dataframe(df_oulu)

st.subheader("Oulunsalo")
st.dataframe(df_oulunsalo)
