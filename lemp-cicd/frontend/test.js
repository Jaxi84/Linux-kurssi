const http = require('http');

function get(path) {
  return new Promise((resolve, reject) => {
    http.get({host: 'localhost', port: 8080, path}, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({statusCode: res.statusCode, body: data}));
    }).on('error', reject);
  });
}

(async () => {
  const r = await get('/health');
  if (r.statusCode !== 200) {
    console.error('FAIL: status', r.statusCode);
    process.exit(1);
  }
  const body = JSON.parse(r.body);
  if (body.status !== 'ok') {
    console.error('FAIL: body', body);
    process.exit(1);
  }
  console.log('PASS: /health ok');
})();
