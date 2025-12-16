FROM python:3.9-slim

WORKDIR /app

# Asennetaan kirjastot
RUN pip install --no-cache-dir streamlit mysql-connector-python pandas python-dotenv plotly

# Kopioidaan tiedostot
COPY . .

# Avataan portti
EXPOSE 8501

# Käynnistyskomento: Sallitaan CORS ja XSRF, jotta toimii IP-osoitteella
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
