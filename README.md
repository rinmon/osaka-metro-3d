# 大阪メトロ リアルタイム 3D マップ

大阪メトロの**実際の運行データ**を表示する3Dウェブアプリです。

## 本番（apl.chotto.news）

| 項目 | URL |
|------|-----|
| 公開ページ | https://apl.chotto.news/tools/osaka-metro-3d/ |
| ポータル | https://apl.chotto.news/ （tools カード） |
| API | `/tools/osaka-metro-3d/api/*` → サーバー `127.0.0.1:5013` |

デプロイ（ポータル側スクリプト）:

```bash
cd "../0000/CHOTTO.NEWS(apl)/apl.chotto.news メニュー構造"
bash scripts/deploy-osaka-metro-3d.sh
```

## 起動（ローカル開発）

```bash
python3 server.py
```

ブラウザで **http://localhost:8123** を開いてください。

`server.py` が静的配信と `/api/*` プロキシを兼ねます。

環境変数:

```bash
export OSAKA_METRO_API_KEY=your_key_here
python3 server.py
# 本番プロキシ単体:
PORT=5013 python3 proxy_api.py
```

## なぜプロキシが必要か

- 大阪メトロの列車位置APIはモバイルアプリ向け内部APIです
- 直接ブラウザから呼ぶとCORSエラーまたは403になります
- クライアントは同一オリジンの `/api/*`（本番は `/tools/osaka-metro-3d/api/*`）のみ呼び、キーはサーバー側のみ

## API エンドポイント

| パス（ローカル） | 本番パス | 説明 |
|------------------|----------|------|
| `/api/trainlocation?route_code=1` | `/tools/osaka-metro-3d/api/trainlocation?...` | 列車位置 |
| `/api/stationCoords` | 同左 | 駅座標 |
| `/api/routeStation` | 同左 | 路線・駅一覧 |
| `/api/route` | 同左 | 路線メタ |

## 記号の見方

- **駅** … 白い円盤＋路線色のリング
- **列車** … 路線色の車体。**三角（コーン）が進行方向**
- **ラベル** … ズームアウト時は主要駅のみ。列車ラベルは近づくと表示

## 機能

- 公式 `routeStation.json` + `stationCoords.json` から路線・駅を自動構築（9路線）
- 実列車位置を3D空間に配置（メッシュ最大160＋動的拡張）
- 約10秒ごとに自動更新
- API障害時は予測 → デモにフォールバック

## データ出典

- 駅座標・路線情報: `static.mobility-operation-info.emetro-app.osakametro.co.jp`
- 列車位置: `api.mobility-operation-info.emetro-app.osakametro.co.jp/app/api/v1/trainlocation`

（非公式利用です。商用利用は自己責任で）

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| ローカルで実データなし | `python3 server.py` を使う（`file://` 不可） |
| 本番で APIキー未設定 | サーバー `api.env` の `OSAKA_METRO_API_KEY` |
| 本番 API 502 | `systemctl status osaka-metro-3d` / ポート 5013 |
| ポート競合（ローカル） | `server.py` の `PORT` を変更 |

---

作成: CHOTTO.NEWS / rinmon (2026)
