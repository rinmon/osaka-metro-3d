const API_KEY = process.env.OSAKA_METRO_API_KEY || 'XSGUG4p5Ya5vQCehV3zZjaDheZAQMpqP9paVan8W';
const API_BASE = 'https://api.mobility-operation-info.emetro-app.osakametro.co.jp/app/api/v1';
const STATIC_BASE = 'https://static.mobility-operation-info.emetro-app.osakametro.co.jp/emetro/cache/common/json';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'X-Api-Key, Content-Type');
}

async function proxyJson(res, url, headers = {}) {
  const upstream = await fetch(url, { headers });
  const body = await upstream.text();
  res.status(upstream.status);
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(body);
}

module.exports = { API_KEY, API_BASE, STATIC_BASE, setCors, proxyJson };
