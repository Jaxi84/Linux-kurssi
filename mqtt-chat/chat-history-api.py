#!/usr/bin/env python3
import os, sys, mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__); CORS(app)

# Ladataan creds.env samasta kansiosta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
creds = {}
try:
    with open(os.path.join(BASE_DIR, "creds.env")) as f:
        for l in f:
            if "=" in l and not l.startswith("#"):
                k, v = l.strip().split("=", 1)
                creds[k.strip()] = v.strip()
except Exception: pass

def get_db():
    return mysql.connector.connect(host=creds.get("DB_HOST"), user=creds.get("DB_USER"), password=creds.get("DB_PASSWORD"), database=creds.get("DB_NAME"))

# Kaksi reittiä varmuuden vuoksi
@app.route("/messages")
@app.route("/api/messages")
def gm():
    try:
        limit = request.args.get("limit", 10, type=int)
        c = get_db(); cur = c.cursor(dictionary=True)
        cur.execute("SELECT nickname, message, created_at FROM messages ORDER BY created_at DESC LIMIT %s", (limit,))
        rows = cur.fetchall(); c.close()
        for r in rows: r["created_at"] = str(r["created_at"])
        return jsonify(rows[::-1])
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == "__main__": app.run(host="0.0.0.0", port=5050)
