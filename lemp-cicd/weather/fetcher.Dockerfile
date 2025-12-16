FROM python:3.12-slim
WORKDIR /app
# riippuvuudet
RUN pip install --no-cache-dir python-dotenv requests mysql-connector-python
# kopioi fetcheri
COPY fetch_weather.py /app/fetch_weather.py
# mahdollistetaan .env:n luku, jos mounttaat sen projektijuuresta
# Ajokomento: ajetaan kerta per käynnistys
