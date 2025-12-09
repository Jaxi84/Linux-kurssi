from flask import Flask, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'mysql'),
        user=os.getenv('DB_USER', 'testiuseri'),
        password=os.getenv('DB_PASSWORD', 'changegqp7jvf@dvw0zmy!ERD'),
        database=os.getenv('DB_NAME', 'appdb')
    )

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/users')
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/init-db')
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            )
        """)
        cursor.execute("""
            INSERT INTO users (name, email) VALUES
            ('John Doe', 'john@example.com'),
            ('Jane Smith', 'jane@example.com')
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Database initialized"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
