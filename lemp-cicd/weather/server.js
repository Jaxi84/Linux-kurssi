const express = require('express');
const app = express();
const mysql = require('mysql2/promise');

const port = process.env.PORT || 8081;

// Compose-verkossa DB_HOST = "db"
const DB_HOST = process.env.DB_HOST || 'db';
const DB_USER = process.env.DB_USER || 'testiuseri';
const DB_PASSWORD = process.env.DB_PASSWORD || 'changeme';
const DB_NAME = process.env.DB_NAME || 'weatherdb';

// Health: kertoo statusin
app.get('/health', (_req, res) => res.json({status: 'ok', ts: new Date().toISOString()}));

// Yhteystesti tietokantaan (KORJATTU taulun nimi: weather_data)
app.get('/health/db', async (_req, res) => {
  try {
    const conn = await mysql.createConnection({
      host: DB_HOST, user: DB_USER, password: DB_PASSWORD, database: DB_NAME
    });
    // Huom: Python loi taulun 'weather_data', ei 'observations'
    const [rows] = await conn.query('SELECT COUNT(*) AS cnt FROM weather_data');
    await conn.end();
    res.json({ db: 'ok', count: rows[0].cnt });
  } catch (err) {
    res.status(500).json({ db: 'fail', error: String(err) });
  }
});

// Etusivu: Listaa säähavainnot tietokannasta
app.get('/', async (_req, res) => {
  let weatherItems = [];
  let error = null;

  try {
    const conn = await mysql.createConnection({
        host: DB_HOST, user: DB_USER, password: DB_PASSWORD, database: DB_NAME
    });
    const [rows] = await conn.query('SELECT city, temperature, description, timestamp FROM weather_data ORDER BY timestamp DESC LIMIT 5');
    await conn.end();
    weatherItems = rows;
  } catch (err) {
    error = String(err);
  }

  // Generoidaan HTML
  const listHtml = weatherItems.map(row => 
    `<li><b>${row.city}</b>: ${row.temperature}°C (${row.description}) <small>${row.timestamp}</small></li>`
  ).join('');

  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Sääsovellus</title>
        <style>
          body { font-family: sans-serif; padding: 2rem; background: #f0f0f0; }
          .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
          h1 { color: #333; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Säähavainnot</h1>
          ${error ? `<p style="color:red">Tietokantavirhe: ${error}</p>` : ''}
          <ul>
            ${listHtml || '<li>Ei havaintoja vielä.</li>'}
          </ul>
          <hr>
          <p><a href="./health">Health Check</a> | <a href="./health/db">DB Check</a></p>
        </div>
      </body>
    </html>
  `);
});

// TÄMÄ PUUTTUI! Käynnistetään palvelin.
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
