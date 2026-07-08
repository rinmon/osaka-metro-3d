# 大阪メトロ リアルタイム 3D マップ

大阪メトロの**実際の運行データ**を表示する3Dウェブアプリです。

## 起動（実データで動かす方法）

```bash
cd osaka-metro-3d

# これだけでOK
python3 server.py
```

ブラウザで **http://localhost:8123** を開いてください。

`server.py` が以下の役割を果たします：
- 静的ファイル（index.html）の配信
- 大阪メトロ公式アプリAPIのプロキシ（CORS + 認証ヘッダ付与）

## なぜプロキシが必要か

- 大阪メトロの列車位置APIはモバイルアプリ向け内部APIです
- 直接ブラウザから呼ぶとCORSエラーまたは403になります
- `server.py` がサーバーサイドで取得して中継しています

## 本番デプロイ（Vercel）

```bash
npx vercel --prod
```

`api/` 以下の Serverless Functions が大阪メトロ API をプロキシします。

## 機能

- 公式 `routeStation.json` + `stationCoords.json` から路線・駅を自動構築（9路線対応）
- 実際の列車位置（from/to駅 + progress）で3D空間に配置（最大120両）
- 約10秒ごとに自動更新
- 路線トグル、視点操作、ホバー情報表示
- APIが取れなかった場合は自動でシミュレーションにフォールバック

## データ出典

- 駅座標・路線情報: `static.mobility-operation-info.emetro-app.osakametro.co.jp`
- 列車位置: `api.mobility-operation-info.emetro-app.osakametro.co.jp/app/api/v1/trainlocation`

（非公式利用です。商用利用は自己責任で）

## トラブルシューティング

- 実データが全く来ない → `python3 server.py` を必ず使ってください
- ポート競合 → `python3 server.py` の PORT = 8123 を変更
- 一部の路線だけ表示されない → その路線の運行が少ない可能性あり

---

作成: CHOTTO.NEWS / rinmon (2026)