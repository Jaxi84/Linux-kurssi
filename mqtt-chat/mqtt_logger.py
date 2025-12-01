
#!/usr/bin/env python3
"""
MQTT → MySQL Logger
- Lukee credentialsit suoraan tekstimuotoisesta creds.env-tiedostosta (key=value).
- Yhdistyy MQTT-brokeriin, tilaa aiheen ja tallentaa JSON-viestit MySQL/MariaDB:hen.

Riippuvuudet (venv:ssä tai järjestelmässä):
  pip install paho-mqtt mysql-connector-python
"""

import os
import json
import time
import logging
import socket
from typing import Dict

import paho.mqtt.client as mqtt
import mysql.connector

#konffit ja utilit
CRED_FILE = os.path.join(os.path.dirname(__file__), "creds.env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mqtt_logger")


def load_creds(path: str) -> Dict[str, str]:
    """
    Lataa key=value -credentialsit tiedostosta.
    - Ohittaa tyhjät rivit ja kommentit (# ...).
    - Trimmaa whitespace:t.
    """
    creds: Dict[str, str] = {}
    if not os.path.isfile(path):
        logger.error(f"Credential-tiedostoa ei löydy: {path}")
        return creds

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                logger.warning(f"Ohitetaan virheellinen rivi credentialsissa: {line}")
                continue
            key, value = line.split("=", 1)
            creds[key.strip()] = value.strip()
    return creds


CREDS = load_creds(CRED_FILE)

# MQTT-config (fallbackit varalta)
MQTT_BROKER = CREDS.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(CREDS.get("MQTT_PORT", "1883"))
MQTT_TOPIC = CREDS.get("MQTT_TOPIC", "chat/messages")

# DB-conf
DB_CONFIG = {
    "host": CREDS.get("DB_HOST", "localhost"),
    "user": CREDS.get("DB_USER", "chat_user"),
    "password": CREDS.get("DB_PASSWORD", ""),
    "database": CREDS.get("DB_NAME", "chat_db"),
}

#DB
def test_db_connection():
    #Kirjoittaa lokiin, onnistuuko DB-yhteys.
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
        logger.info("yhteys kantaan OK")
    except mysql.connector.Error as err:
        logger.error(f"Ei yhteyttä db: {err}")


def save_message(nickname: str, message: str, client_id: str) -> None:
    """Tallenna viesti messages-tauluun."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (nickname, message, client_id)
            VALUES (%s, %s, %s)
            """,
            (nickname, message, client_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Tallennettu: <{nickname}> ({client_id}) {message[:60]}{'...' if len(message)>60 else ''}")
    except mysql.connector.Error as err:
        logger.error(f"Tietokantavirhe: {err}")

#MQTT callbackit
def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None):
    if rc == mqtt.MQTT_ERR_SUCCESS:
        logger.info(f"Yhdistetty MQTT-brokeriin {MQTT_BROKER}:{MQTT_PORT} (rc={rc})")
        result, mid = client.subscribe(MQTT_TOPIC, qos=0)
        if result == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Tilattu aihe: {MQTT_TOPIC}")
        else:
            logger.error(f"Subscribe epäonnistui, code={result}")
    else:
        logger.error(f"Yhteysvirhe MQTT-brokeriin, rc={rc}")


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    try:
        payload_str = msg.payload.decode("utf-8", errors="replace")
        logger.info(f"Viesti korvanappiin: {payload_str}")

        data = json.loads(payload_str)

        nickname = str(data.get("nickname", "John Doe"))[:50]
        text     = str(data.get("text", ""))                 # tallennetaan sellaisenaan
        client_id = str(data.get("clientId", ""))[:100]

        if not text:
            logger.warning("Viestin 'text' kenttä uupui, ei tallenneta.")
            return

        save_message(nickname, text, client_id)

    except json.JSONDecodeError:
        logger.warning(f"Virheellinen JSON: {msg.payload!r}")
    except Exception as e:
        logger.error(f"Virhe viestin käsittelyssä: {e}")


def on_disconnect(client: mqtt.Client, userdata, rc, properties=None):
    # rc != 0 → tahaton katkeaminen
    logger.warning(f"Yhteys katkaistu (rc={rc}). Uudelleenyhdistys yrittää...")


###- MAIN -###

def main():
    # Pieni diagnostiikka:
    logger.info(f"Hostname: {socket.gethostname()}")
    logger.info(f"Käytettävä broker: {MQTT_BROKER}:{MQTT_PORT}")
    logger.info(f"Tilausaihe: {MQTT_TOPIC}")
    logger.info(f"DB config: host={DB_CONFIG['host']} db={DB_CONFIG['database']} user={DB_CONFIG['user']}")

    test_db_connection()

    # Luo MQTT-cleintti:
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"mqtt_logger_{int(time.time())}",
        clean_session=True,
    )

    # Callbackit
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    #reconnect delayt
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    # Yhdistä ja blokkaa ikuisesti
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Sammutetaan...")
        try:
            client.disconnect()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Ei saatu yhteyttä MQTT-brokeriin: {e}")


if __name__ == "__main__":
    main()
