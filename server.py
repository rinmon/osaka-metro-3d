#!/usr/bin/env python3
"""
大阪メトロ リアルタイム3Dマップ ローカルサーバー + APIプロキシ

使い方:
  cd osaka-metro-3d
  python3 server.py

  ブラウザで http://localhost:8123 を開く

これでCORSや認証の問題なく実際の運行データを取得できます。
"""

import http.server
import urllib.request
import urllib.error
import json
import socketserver
import time
from urllib.parse import urlparse, parse_qs

PORT = 8123
API_KEY = "XSGUG4p5Ya5vQCehV3zZjaDheZAQMpqP9paVan8W"
API_BASE = "https://api.mobility-operation-info.emetro-app.osakametro.co.jp/app/api/v1"
STATIC_BASE = "https://static.mobility-operation-info.emetro-app.osakametro.co.jp/emetro/cache/common/json"

class OsakaProxyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # ローカル開発用にCORSを許可
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Api-Key, Content-Type")

        # 開発時はキャッシュを無効化して、index.htmlの変更を即反映
        if self.path in ('/', '/index.html') or not self.path.startswith('/api/'):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")

        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        # 実際の列車位置APIのプロキシ
        if parsed.path.startswith("/api/trainlocation"):
            qs = parse_qs(parsed.query)
            route_code = qs.get("route_code", ["1"])[0]
            self._proxy_trainlocation(route_code)
            return

        # 駅座標データ（公開だがプロキシ経由でCORS問題を避ける）
        if parsed.path.startswith("/api/stationCoords"):
            self._proxy_static(f"{STATIC_BASE}/stationCoords.json")
            return

        if parsed.path.startswith("/api/routeStation"):
            self._proxy_static(f"{STATIC_BASE}/routeStation.json")
            return

        if parsed.path.startswith("/api/route"):
            self._proxy_static(f"{STATIC_BASE}/route.json")
            return

        # それ以外は通常の静的ファイル配信（index.htmlなど）
        super().do_GET()

    def _proxy_trainlocation(self, route_code):
        url = f"{API_BASE}/trainlocation?route_code={route_code}"
        try:
            req = urllib.request.Request(
                url,
                headers={"X-Api-Key": API_KEY}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Proxy error: {str(e)}"}).encode())

    def _proxy_static(self, url):
        try:
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        # シンプルなログ
        print(f"[server] {args[0]}")


def main():
    # 開発用：ポート再利用を許可（再起動時の Address already in use を避ける）
    socketserver.TCPServer.allow_reuse_address = True

    httpd = None
    for attempt in range(5):
        try:
            httpd = socketserver.TCPServer(("", PORT), OsakaProxyHandler)
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"[server] Port {PORT} busy, retrying in 0.5s... ({attempt+1}/5)")
                time.sleep(0.5)
            else:
                raise
    if httpd is None:
        print(f"[server] Failed to bind port {PORT} after retries")
        return

    with httpd:
        print(f"大阪メトロ 3D サーバー起動: http://localhost:{PORT}")
        print("実データ取得用プロキシも同時に動いています。")
        print("Ctrl+C で停止")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n停止しました。")


if __name__ == "__main__":
    main()