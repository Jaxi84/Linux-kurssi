const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

// Logittaa pyynnöt (hyödyllinen vianetsinnässä)
app.use((req, res, next) => {
  console.log(`Request: ${req.method} ${req.url}`);
  next();
});

// --- API ---
app.get('/api/version', (_req, res) => {
  res.json({ version: process.env.APP_VERSION || '1.0.0' });
});

app.get('/api/time', (_req, res) => {
  res.json({ nowUtc: new Date().toISOString() });
});

app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date()
  });
});

// --- UI ---
app.get('/', (_req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>CICD App</title>
        <style>
            body { font-family: sans-serif; padding: 2rem; background: #f0f0f0; }
            .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            li { margin-bottom: 5px; }
            a { text-decoration: none; color: #007bff; font-weight: bold; }
            a:hover { text-decoration: underline; }
        </style>
      </head>
      <body>
        <div class="container">
           <h1>LEMP CICD Demo Toimii! 🚀</h1>
           <p>Tämä vastaus tulee Node.js-kontista.</p>
           <hr>
           <p><strong>Sovellukset:</strong></p>
           <ul>
             <li style="font-size: 1.1em; margin-bottom: 15px;">
                🌤️ <strong>Sääsovellus: <a href="/weather/">Siirry tästä (/weather/)</a></strong>
             </li>
             
             <p><strong>Tekniset API-tarkistukset:</strong></p>
             <li>Juuri: <code>/</code></li>
             <li>Health: <a href="./health">/health</a></li>
             <li>Version: <a href="./api/version">/api/version</a></li>
             <li>Time: <a href="./api/time">/api/time</a></li>
           </ul>
        </div>
      </body>
    </html>
  `);
});

app.listen(port, () => {
  console.log(`Serveri käynnistyi portissa :${port}`);
});
