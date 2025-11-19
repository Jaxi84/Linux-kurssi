#!/bin/bash
# Polku virtuaaliympäristöön
VENV_DIR="/home/ubuntu/myapiapp/venv"
REQ_FILE="/home/ubuntu/myapiapp/requirements.txt"
ENV_FILE="/home/ubuntu/myapiapp/cred.env"
PY_FILE="/home/ubuntu/myapiapp/fetch_weather.py"


# Luo virtuaaliympäristö, jos ei ole olemassa
if [ ! -d "$VENV_DIR" ]; then
    echo "Luodaan virtuaaliympäristö..."
    python3 -m venv $VENV_DIR
fi

# Aktivoi virtuaaliympäristö
source $VENV_DIR/bin/activate

# Asenna riippuvuudet requirements.txt-tiedostosta
if [ -f "$REQ_FILE" ]; then
    echo "Asennetaan riippuvuudet..."
    pip install --upgrade pip
    pip install -r $REQ_FILE
else
    echo "requirements.txt ei löytynyt!"
fi

# Suorita fetch_weather.py
if [ -f "$PY_FILE" ]; then
    echo "Suoritetaan fetch_weather.py..."
    python $PY_FILE
else
    echo "fetch_weather.py ei löytynyt!"
fi

echo "Valmis!"
