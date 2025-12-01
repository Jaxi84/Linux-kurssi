
#!/usr/bin/env python3
"""
MQTT Chat -tilaaja
- Tilaa aiheen "chat/messages"
- Parsii JSON-payloadin ja tulostaa siististi
- Yrittää uudelleenyhdistystä automaattisesti
"""

import json
import sys
import time
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost" #vaihda tarvittaessa  "86.50.21.26"
PORT = 1883
TOPIC = "chat/messages"
CLIENT_ID = f"python-subscriber-{int(time.time())}"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[INFO] Yhdistetty brokeriin {BROKER}:{PORT}, tilataan aihe '{TOPIC}'")
        client.subscribe(TOPIC, qos=0)
    else:
        print(f"[ERROR] Yhteys epäonnistui, rc={rc}")

def pretty_print_message(payload_bytes):
    try:
        payload = payload_bytes.decode("utf-8", errors="replace")
        data = json.loads(payload)
        nickname = data.get("nickname", "Tuntematon")
        text = data.get("text", "")
        client_id = data.get("clientId", "")
        ts = data.get("timestamp", None)
        if ts is not None:
            # jos timestamp millisekunteina:
            if ts > 10**12:
                dt = datetime.fromtimestamp(ts / 1000.0)
            else:
                dt = datetime.fromtimestamp(ts)
            ts_str = dt.isoformat(sep=" ", timespec="seconds")
        else:
            ts_str = datetime.now().isoformat(sep=" ", timespec="seconds")

        print(f"[{ts_str}] <{nickname}> ({client_id}): {text}")
    except json.JSONDecodeError:
        # ei-JSON viesti, tulosta sellaisenaan
        print(f"[RAW] {payload_bytes}")
    except Exception as e:
        print(f"[ERROR] Viestin käsittelyssä virhe: {e}", file=sys.stderr)

def on_message(client, userdata, msg):
    pretty_print_message(msg.payload)

def on_disconnect(client, userdata, rc):
    print(f"[WARN] Yhteys katkaistu (rc={rc}). Yritetään uudelleenyhdistystä...")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # (Valinnainen) keepalive & automaattinen uudelleenyhdistys:
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Sammutetaan...")
        client.disconnect()
    except Exception as e:
        print(f"[ERROR] Ei saatu yhteyttä: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
