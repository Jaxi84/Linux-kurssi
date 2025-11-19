import configparser
import mysql.connector
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    db_time = None
    error_msg = None

    try:
        config = configparser.ConfigParser()
        config.read('config.ini') #ajetaan credentialit config.inistä

        conn = mysql.connector.connect( #näillä nimillä config.inissä
            host=config.get('database', 'host'),
            user=config.get('database', 'user'),
            password=config.get('database', 'password'),
            database=config.get('database', 'db')
        )

        cursor = conn.cursor()
        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()

        if result:
            db_time = result[0].strftime('%Y-%m-%d %H:%M:%S') #näytetään aika

        cursor.close()
        conn.close()

    except Exception as err: #jotain meni pieleen
        error_msg = f"Virhe: {err}"

    return render_template('index.html', db_time=db_time, error=error_msg) #palautellaan toivon mukaan kellonaika

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/data-analysis')
def data_analysis():
    return render_template('data_analysis.html', title="Viikko tehtävä 3 - Streamlit")
