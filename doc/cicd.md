# 🚀 Lambda用CI/CD構築指示書（GitHub Actions）

---

## 🎯 目的

GitHub Actionsを用いて、`main`ブランチへのpushをトリガーに以下を自動実行します：

- `sam build` によるLambda関数のビルド  
- `sam deploy` による本番環境へのデプロイ

---

## 📁 ディレクトリ構成（CI/CD）

```
.github/
└── workflows/
    └── deploy.yml
```

---

## 🛠 必要準備（Secrets）

GitHubリポジトリの「Settings > Secrets and variables > Actions」に以下のシークレットを登録してください：

| シークレット名 | 説明 |
|----------------|------|
| AWS_ACCESS_KEY_ID | デプロイに使うIAMユーザーのアクセスキー |
| AWS_SECRET_ACCESS_KEY | 上記ユーザーのシークレットキー |
| AWS_REGION | 例: `ap-northeast-1` |
| STACK_NAME | 例: `open-meteo-api-stack` |

※ IAMユーザーには `cloudformation:*`, `lambda:*`, `s3:PutObject` などが許可されている必要があります。

---

## 📄 `.github/workflows/deploy.yml`

以下の内容で作成してください：

```yaml
name: Deploy Lambda with SAM

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install AWS SAM CLI
        uses: aws-actions/setup-sam@v2

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt || echo "No global requirements"

      - name: Build with SAM
        run: sam build

      - name: Deploy with SAM
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
        run: |
          sam deploy \
            --stack-name ${{ secrets.STACK_NAME }} \
            --region ${{ secrets.AWS_REGION }} \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset \
            --capabilities CAPABILITY_IAM \
            --resolve-s3
```

---

## ✅ 成功の定義

- `main`ブランチにコードをpushすると自動でビルド・デプロイされる  
- GitHub Actionsのログに `sam deploy` の成功出力が確認できる  
- Lambda関数が更新され、S3への出力に反映される  

---

## 🧪 補足（テスト戦略）

- ステージング環境を導入する場合、`STACK_NAME`を `open-meteo-api-stack-staging` などにして、ブランチ単位で分ける構成も可能です。

---

## 📜 注意点

- `samconfig.toml` がある場合、コマンドをさらに簡略化できます。  
- 認証情報（IAMキー）は最小権限で設定し、外部に漏らさないよう注意してください。

---
