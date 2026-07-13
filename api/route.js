const { STATIC_BASE, setCors, proxyJson } = require('./_lib');

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  try {
    await proxyJson(res, `${STATIC_BASE}/route.json`);
  } catch (e) {
    res.status(502).json({ error: `Proxy error: ${e.message}` });
  }
};
