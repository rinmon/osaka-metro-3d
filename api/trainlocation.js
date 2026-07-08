const { getApiKey, API_BASE, setCors, proxyJson } = require('./_lib');

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  const apiKey = getApiKey();
  if (!apiKey) {
    res.status(503);
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify({ error: 'OSAKA_METRO_API_KEY is not configured' }));
    return;
  }

  const routeCode = req.query.route_code || '1';
  try {
    await proxyJson(res, `${API_BASE}/trainlocation?route_code=${encodeURIComponent(routeCode)}`, {
      'X-Api-Key': apiKey,
    });
  } catch (e) {
    res.status(502).json({ error: `Proxy error: ${e.message}` });
  }
};
