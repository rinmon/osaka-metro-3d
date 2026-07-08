# 大阪メトロ リアルタイム 3D マップ

大阪メトロの**実際の運行データ**を表示する3Dウェブアプリです。

## 起動（ローカル開発）

```bash
cd osaka-metro-3d

# これだけでOK（APIキーは server.py に内蔵フォールバックあり）
python3 server.py
```

ブラウザで **http://localhost:8123** を開いてください。

`server.py` が以下の役割を果たします：
- 静的ファイル（index.html）の配信
- 大阪メトロ公式アプリAPIのプロキシ（CORS + 認証ヘッダ付与）

環境変数で API キーを上書きする場合：

```bash
cp .env.example .env
# .env に OSAKA_METRO_API_KEY=... を設定
export OSAKA_METRO_API_KEY=your_key_here
python3 server.py
```

## なぜプロキシが必要か

- 大阪メトロの列車位置APIはモバイルアプリ向け内部APIです
- 直接ブラウザから呼ぶとCORSエラーまたは403になります
- `server.py`（ローカル）または `api/`（Vercel）がサーバーサイドで取得して中継しています
- クライアント（index.html）は常に同一オリジンの `/api/*` を使用し、APIキーを露出しません

## 本番デプロイ（Vercel）

### 前提

- [Vercel](https://vercel.com) アカウント
- GitHub リポジトリ: https://github.com/rinmon/osaka-metro-3d
- 大阪メトロ API キー（`OSAKA_METRO_API_KEY`）

### 手順 1: Vercel にログイン・リンク

```bash
npx vercel login
npx vercel link   # 初回のみ。GitHub リポジトリと紐付け
```

### 手順 2: 環境変数を設定

Vercel Dashboard → プロジェクト → **Settings** → **Environment Variables**

| Name | Value | Environment |
|------|-------|-------------|
| `OSAKA_METRO_API_KEY` | （大阪メトロ API キー） | Production, Preview, Development |

CLI から設定する場合：

```bash
npx vercel env add OSAKA_METRO_API_KEY production
```

### 手順 3: 本番デプロイ

```bash
npx vercel --prod --yes
```

デプロイ成功後、CLI に表示される URL が本番 URL です（例: `https://osaka-metro-3d.vercel.app`）。

### GitHub Actions による自動デプロイ（代替）

対話的な `vercel login` が使えない場合、GitHub Secrets を設定して `main` への push で自動デプロイできます。

**必要な Secrets（GitHub → Settings → Secrets and variables → Actions）:**

| Secret | 取得方法 |
|--------|----------|
| `VERCEL_TOKEN` | Vercel → Account Settings → Tokens |
| `VERCEL_ORG_ID` | `npx vercel link` 後の `.vercel/project.json` の `orgId` |
| `VERCEL_PROJECT_ID` | 同上の `projectId` |

`VERCEL_TOKEN` が設定されていれば、`.github/workflows/deploy-vercel.yml` が push 時に本番デプロイを実行します。

## API エンドポイント

| パス | 説明 |
|------|------|
| `/api/trainlocation?route_code=1` | 列車位置（要 API キー） |
| `/api/stationCoords` | 駅座標（静的 JSON プロキシ） |
| `/api/routeStation` | 路線・駅一覧（静的 JSON プロキシ） |
| `/api/route` | 路線メタ情報（静的 JSON プロキシ） |

`server.py` では `routeStation` を `route` より先にマッチさせています（Vercel もファイル名で自動ルーティング）。

## 機能

- 公式 `routeStation.json` + `stationCoords.json` から路線・駅を自動構築（9路線対応）
- 実際の列車位置（from/to駅 + progress）で3D空間に配置（最大120両）
- 約10秒ごとに自動更新
- 路線トグル、視点操作、ホバー情報表示
- APIが取れなかった場合は過去データ予測 → デモシミュレーションにフォールバック

## データ出典

- 駅座標・路線情報: `static.mobility-operation-info.emetro-app.osakametro.co.jp`
- 列車位置: `api.mobility-operation-info.emetro-app.osakametro.co.jp/app/api/v1/trainlocation`

（非公式利用です。商用利用は自己責任で）

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| 実データが全く来ない（ローカル） | `python3 server.py` を必ず使う（`file://` では動かない） |
| 本番で「APIキー未設定」 | Vercel に `OSAKA_METRO_API_KEY` を設定して再デプロイ |
| `vercel login` 失敗 | GitHub Actions + `VERCEL_TOKEN` を使用 |
| ポート競合 | `server.py` の `PORT = 8123` を変更 |
| 一部の路線だけ表示されない | その路線の運行が少ない可能性あり |

---

作成: CHOTTO.NEWS / rinmon (2026)
