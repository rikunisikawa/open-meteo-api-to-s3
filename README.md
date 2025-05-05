# ☁️ Lambdaによる気圧データ収集・S3保存タスク  
**🧠 AIエージェント向け実装指示書**

---

## 📦 対象GitHubリポジトリ

このプロジェクトは、以下のリポジトリで管理されています：

🔗 **GitHubリポジトリ**：  
👉 `https://github.com/rikunisikawa/open-meteo-api-to-s3.git`

プロジェクト開始時に `git init` → `add` → `commit` → `branch main 作成` → `GitHub に push` まで一貫して実施してください。

---

## 🎯 プロジェクトの目的

無料API（Open-Meteo）から1時間ごとに気圧データを取得し、AWS S3に保存するLambda関数を作成します。データは別のRuby on Railsアプリケーションから取得され、MySQLへ取り込まれます。

**このLambdaは、APIデータ取得〜S3保存までの処理を担います。**

---

## ✅ あなたの作業内容

### 1. Gitリポジトリ初期化と同期

```bash
git init
git remote add origin https://github.com/rikunisikawa/open-meteo-api-to-s3.git
echo "# open-meteo-api-to-s3" >> README.md
git add .
git commit -m "Initial commit: setup project for Open-Meteo → S3 Lambda"
git branch -M main
git push -u origin main
```

---

### 2. ディレクトリ構成（SAMプロジェクト）

```
open-meteo-api-to-s3/
├── app/
│   └── fetch_pressure.py
├── requirements.txt
├── template.yaml
├── README.md
```

---

### 3. Lambda関数（`app/fetch_pressure.py`）

#### 機能：
- Open-Meteo APIから気圧データを取得
- 現在の時刻に最も近いデータを抽出
- JSON形式に変換し、次のキーでS3に保存：
  ```
  s3://<バケット名>/pressure/YYYY/MM/DD/HH.json
  ```

#### 保存例：

```json
{
  "recorded_at": "2025-05-03T14:00:00Z",
  "pressure": 1013.2,
  "location": "Tokyo"
}
```

- 環境変数で以下を受け取るようにする：
  - `BUCKET_NAME`
  - `LATITUDE`
  - `LONGITUDE`
  - `LOCATION_NAME`

---

### 4. SAMテンプレート（`template.yaml`）

- ランタイムは `python3.11`
- IAMロールは `s3:PutObject` 権限を持つ
- 環境変数（上記）を渡す
- Lambda名は `FetchPressureFunction`

---

### 5. requirements.txt

以下を最低限含めてください：

```txt
boto3
requests
```

---

### 6. 動作確認（ローカル）

```bash
sam build
sam local invoke FetchPressureFunction --event events/event.json
```

---

### 7. S3設計指針（Railsアプリとの連携前提）

| 項目 | 内容 |
|------|------|
| キー形式 | `pressure/YYYY/MM/DD/HH.json` |
| 保存形式 | JSON（1レコード/1ファイル） |
| データ構造 | `recorded_at`, `pressure`, `location` |
| 目的 | Railsアプリ側が定期取得してMySQLに蓄積・可視化 |
| 前提 | 時刻はISO 8601形式、日次の粒度で連携が可能な構造に |

---

### 8. SAMデプロイ手順 (1回目)

```bash
sam deploy --guided
```

#### 実行例

```text
Stack Name: open-meteo-api-stack
AWS Region: ap-northeast-1
Confirm changes before deploy: Y
Allow SAM CLI IAM role creation: Y
Save arguments to samconfig.toml: Y
```

---

### 8. SAMデプロイ手順 (2回目以降)

```bash
sam deploy
```

---

## ✅ 成功の定義 (Definition of Done)

- GitHubのリポジトリにLambdaコード、SAMテンプレート、READMEが含まれている
- 気圧データがS3にISO8601形式で正しく保存される
- 環境変数で設定を変更可能
- 1時間ごとにEventBridgeで自動実行

---

## 📜 注意点

- 無料APIのため、リクエスト頻度は1時間に1回まで
- `print()` でCloudWatch Logsにログを出力
- S3キー名やJSON構造はRails連携のため厳密
- S3側のバージョニング/ライフサイクルは後日検討
