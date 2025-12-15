const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

app.get('/health', (_req, res) => res.json({status: 'ok'}));

app.get('/', (_req, res) => {
  res.send(`
    <html><head><title>CICD app</title></head>
    <body>
      <h1>LEMP CICD demo</h1>
      <p>Polku: /cicd</p>
      <p>Health: /health/health</a></p>
    </body></html>
  `);
});

app.listen(port, () => console.log(`App on :${port}`));
