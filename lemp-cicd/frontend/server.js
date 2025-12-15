const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

// (Valinnainen) Lokitetaan pyynnöt konsoliin debuggausta varten
app.use((req, res, next) => {
  console.log(`Pyyntö saapui: ${req.method} ${req.url}`);
  next();
});

// Health-check (Tätä voi käyttää testiskriptissä)
app.get('/health', (_req, res) => {
  res.json({ 
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date()
  });
});

// Juurisivu (näkyy selaimessa osoitteessa /cicd/)
app.get('/', (_req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>CICD App</title>
        <style>
            body { font-family: sans-serif; padding: 2rem; background: #f0f0f0; }
            .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        </style>
      </head>
      <body>
        <div class="container">
           <h1>LEMP CICD Demo Toimii! 🚀</h1>
           <p>Tämä vastaus tulee Node.js-kontista.</p>
           <hr>
           <p><strong>Linkit:</strong></p>
           <ul>
             <li>Sovelluksen juuri: <code>/cicd/</code></li>
             <li>Terveystarkistus: <a href="./health">/cicd/health</a> (JSON)</li>
           </ul>
        </div>
      </body>
    </html>
  `);
});

// Käynnistä palvelin
app.listen(port, () => {
  console.log(`Serveri käynnistyi portissa :${port}`);
});
