const { API_KEY, API_BASE, setCors, proxyJson } = require('./_lib');

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  const routeCode = req.query.route_code || '1';
  try {
    await proxyJson(res, `${API_BASE}/trainlocation?route_code=${encodeURIComponent(routeCode)}`, {
      'X-Api-Key': API_KEY,
    });
  } catch (e) {
    res.status(502).json({ error: `Proxy error: ${e.message}` });
  }
};
