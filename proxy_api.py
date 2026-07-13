#!/usr/bin/env python3
"""
大阪メトロ API プロキシのみ（apl.chotto.news 本番用）

  PORT=5013 OSAKA_METRO_API_KEY=... python3 proxy_api.py

nginx:
  location /tools/osaka-metro-3d/api/ {
    proxy_pass http://127.0.0.1:5013/api/;
  }
"""

from __future__ import annotations

import json
import os
import socketserver
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", "5013"))
API_KEY = os.environ.get("OSAKA_METRO_API_KEY", "")
API_BASE = "https://api.mobility-operation-info.emetro-app.osakametro.co.jp/app/api/v1"
STATIC_BASE = "https://static.mobility-operation-info.emetro-app.osakametro.co.jp/emetro/cache/common/json"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[osaka-metro-api] {args[0]}")

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Api-Key, Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/health", "/api/health"):
            self._json(200, {"ok": True, "service": "osaka-metro-3d-api"})
            return

        if path.startswith("/api/trainlocation"):
            if not API_KEY:
                self._json(503, {"error": "OSAKA_METRO_API_KEY is not configured"})
                return
            route_code = parse_qs(parsed.query).get("route_code", ["1"])[0]
            self._proxy(
                f"{API_BASE}/trainlocation?route_code={route_code}",
                headers={"X-Api-Key": API_KEY},
            )
            return

        if path.startswith("/api/stationCoords"):
            self._proxy(f"{STATIC_BASE}/stationCoords.json")
            return

        if path.startswith("/api/routeStation"):
            self._proxy(f"{STATIC_BASE}/routeStation.json")
            return

        if path.startswith("/api/route"):
            self._proxy(f"{STATIC_BASE}/route.json")
            return

        self._json(404, {"error": "not found", "path": path})

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _proxy(self, url, headers=None):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            self._json(e.code, {"error": str(e)})
        except Exception as e:
            self._json(502, {"error": f"Proxy error: {e}"})


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"osaka-metro-3d API proxy on http://127.0.0.1:{PORT}")
        if not API_KEY:
            print("WARNING: OSAKA_METRO_API_KEY is empty — trainlocation will return 503")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
