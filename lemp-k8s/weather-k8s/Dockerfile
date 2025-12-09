FROM python:3.9-slim

WORKDIR /app

# Asenna riippuvuudet
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopioi koodit
COPY . .

# Oletuskomento (voidaan ylikirjoittaa Kubernetesissa)
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
