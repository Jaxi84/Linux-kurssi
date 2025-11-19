import configparser
import mysql.connector
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Analysis", page_icon="📊", layout="wide")

@st.cache_data(ttl=60)
def get_connection_params():
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    return {
        "host": cfg.get("database", "host", fallback="127.0.0.1"),
        "user": cfg.get("database", "user"),
        "password": cfg.get("database", "password"),
        "database": "lefa_db",
    }

def query_df(sql, params=None):
    cp = get_connection_params()
    conn = mysql.connector.connect(**cp)
    try:
        df = pd.read_sql(sql, con=conn, params=params)
    finally:
        conn.close()
    return df

def main():
    st.title("Data Analysis (MySQL)")
    st.markdown("Tää Streamlit-näkymä on Nginxin takana polussa `/data-analysis`.")

    with st.sidebar:
        st.header("Valinnat")
        table = st.text_input("Taulun nimi", value="lefa")
        limit = st.slider("Rivimäärä", 1, 1000, 50)

    try:
        df = query_df(f"SELECT * FROM {table} LIMIT %s", params=(limit,))
        st.success(f"Noudettu {len(df)} riviä taulusta `{table}`")
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.select_dtypes(include="number"))
    except Exception as e:
        st.error(f"Virhe datan noudossa: {e}")

if __name__ == "__main__":
    main()
