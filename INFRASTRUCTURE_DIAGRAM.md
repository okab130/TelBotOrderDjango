# テスト環境インフラ構成図

## 📋 概要

このドキュメントでは、Telegram Bot注文システムのテスト環境におけるインフラ構成と、ngrokの役割について説明します。

---

## 🏗️ インフラ構成図

```
┌─────────────────────────────────────────────────────────────────────┐
│                         インターネット                                  │
└─────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    │                             │
         ┌──────────▼──────────┐      ┌──────────▼──────────┐
         │  Telegram Server    │      │   ngrok Cloud       │
         │                     │      │                     │
         │  - Botメッセージ受信  │      │  - トンネルサービス   │
         │  - Webhook送信      │      │  - HTTPS証明書      │
         │  - ユーザー管理      │      │  - 公開URL発行      │
         └──────────┬──────────┘      └──────────┬──────────┘
                    │                             │
                    │ ③ Webhook POST             │ ① HTTPSトンネル
                    │ (HTTPS)                     │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   ngrok Agent (ローカル)     │
                    │   - ポート: 4040 (UI)       │
                    │   - トンネル管理            │
                    └──────────────┬──────────────┘
                                   │
                                   │ ② ローカル転送
                                   │ (HTTP)
                    ┌──────────────▼──────────────┐
                    │     開発用PC (localhost)     │
                    │                             │
┌───────────────────┴─────────────────────────────┴───────────────────┐
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Django開発サーバー (0.0.0.0:8000)                           │  │
│  │                                                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │  REST API    │  │ Telegram Bot │  │  管理画面     │     │  │
│  │  │  /api/       │  │  /telegram/  │  │  /admin/     │     │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │  │
│  │         │                 │                 │             │  │
│  │         └────────┬────────┴─────────────────┘             │  │
│  │                  │                                        │  │
│  │         ┌────────▼────────┐                               │  │
│  │         │  Django ORM     │                               │  │
│  │         └────────┬────────┘                               │  │
│  │                  │                                        │  │
│  │         ┌────────▼────────┐                               │  │
│  │         │  SQLite DB      │                               │  │
│  │         │  (db.sqlite3)   │                               │  │
│  │         └─────────────────┘                               │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  静的ファイル・メディア                                       │  │
│  │                                                             │  │
│  │  /media/                                                    │  │
│  │    ├── qrcodes/          (QRコード画像)                     │  │
│  │    └── menu_images/      (メニュー画像)                     │  │
│  │                                                             │  │
│  │  /static/                                                   │  │
│  │    ├── admin/            (Django管理画面用)                 │  │
│  │    └── miniapp/          (Telegram Mini Apps用)            │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           開発環境PC
```

---

## 🔄 データフロー

### 1. ユーザーがBotにメッセージ送信

```
Telegramアプリ (ユーザー)
  │
  │ メッセージ送信
  │
  ▼
Telegram Server
  │
  │ Webhook POST (HTTPS)
  │ POST https://abc123.ngrok-free.app/telegram/webhook/
  │
  ▼
ngrok Cloud
  │
  │ HTTPSを復号化してHTTPに変換
  │
  ▼
ngrok Agent (ローカル)
  │
  │ localhost:8000 に転送
  │
  ▼
Django開発サーバー
  │
  │ telegram_bot/views.py で処理
  │
  ▼
Bot Handler
  │
  │ 応答メッセージ作成
  │
  ▼
Telegram API (直接)
  │
  ▼
Telegramアプリ (ユーザー)
```

### 2. QRコード経由でMini Apps起動

```
QRコード
  │ スキャン
  ▼
Telegram リンク
  │ 例: https://t.me/mobail_order_bot?start=table-A-1
  ▼
Telegram Server
  │
  │ /start コマンド実行
  │
  ▼
(上記のWebhookフロー)
  │
  ▼
Bot応答でMini Apps URLを送信
  │ 例: https://abc123.ngrok-free.app/miniapp/?table_id=1
  ▼
ユーザーがMini Appsボタンをクリック
  │
  ▼
ngrok経由でDjangoサーバーにアクセス
  │
  ▼
miniapp.html レンダリング
  │
  ▼
注文画面表示
```

---

## 🌐 ngrokの役割

### ngrokとは？

**ngrok**は、ローカルで動作している開発サーバーを、インターネット上に公開するためのトンネルサービスです。

### なぜngrokが必要か？

Telegram Botの**Webhook**は以下の要件があります：

1. ✅ **HTTPS**が必須（HTTPは不可）
2. ✅ **公開アクセス可能**なURLが必要
3. ✅ **有効なSSL証明書**が必要

ローカル開発環境（`localhost:8000`）は：
- ❌ インターネットから直接アクセス不可
- ❌ HTTPSではない
- ❌ SSL証明書がない

**ngrokがこれらの問題を解決します！**

### ngrokの仕組み

```
Telegram Server
  │
  │ ③ HTTPS リクエスト
  │ https://abc123.ngrok-free.app/telegram/webhook/
  │
  ▼
┌─────────────────────────────┐
│   ngrok Cloud Server        │
│                             │
│  - HTTPS終端（SSL復号化）    │
│  - 公開URL管理               │
│  - トラフィック転送           │
└─────────────┬───────────────┘
              │
              │ ① セキュアトンネル
              │ (暗号化接続)
              │
              ▼
┌─────────────────────────────┐
│   ngrok Agent (PC上)        │
│                             │
│  - ローカルで実行            │
│  - ポート4040でUI提供        │
└─────────────┬───────────────┘
              │
              │ ② HTTP転送
              │ http://localhost:8000
              │
              ▼
┌─────────────────────────────┐
│   Django開発サーバー         │
│   (0.0.0.0:8000)           │
└─────────────────────────────┘
```

---

## 🔧 ngrokの使用箇所

### 1. Telegram Webhook設定

```python
# .env ファイル
TELEGRAM_WEBHOOK_URL=https://abc123.ngrok-free.app

# Django管理コマンド
python manage.py set_telegram_webhook
```

実際のWebhook URL:
```
https://abc123.ngrok-free.app/telegram/webhook/
```

### 2. Mini Apps URLの生成

```python
# QRコード生成時
qr_url = f"https://t.me/{BOT_USERNAME}?start=table-{table.table_number}"

# Bot応答時
miniapp_url = f"{settings.TELEGRAM_WEBHOOK_URL}/miniapp/?table_id={table.id}"
```

### 3. メディアファイル配信

```python
# メニュー画像URL
https://abc123.ngrok-free.app/media/menu_images/pizza.jpg

# QRコード画像URL
https://abc123.ngrok-free.app/media/qrcodes/table_1_A-1.png
```

---

## 📝 ngrok登録・設定手順

### ステップ1: アカウント登録（無料）

1. **ngrok公式サイトにアクセス**
   - https://dashboard.ngrok.com/signup

2. **アカウント作成**
   - Googleアカウントでサインアップ（推奨）
   - GitHubアカウントでサインアップ
   - またはメールアドレスで登録

3. **無料プラン**
   - ✅ 1つのアクティブトンネル
   - ✅ ランダムURL（再起動のたびに変更）
   - ✅ 月40,000リクエスト
   - ✅ HTTPS対応

### ステップ2: Authtoken取得

1. ダッシュボードにログイン
2. "Your Authtoken"セクションに移動
3. Authtokenをコピー（例: `2abc123def456ghi789jkl`）

### ステップ3: インストール

#### Windows
```bash
# 公式サイトからダウンロード
https://ngrok.com/download

# zipを解凍してngrok.exeを配置
# 推奨: C:\tools\ngrok\ngrok.exe
```

#### macOS (Homebrew)
```bash
brew install ngrok/ngrok/ngrok
```

#### Linux
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null

echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list

sudo apt update && sudo apt install ngrok
```

### ステップ4: Authtoken設定

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

例:
```bash
ngrok config add-authtoken 2abc123def456ghi789jkl
```

### ステップ5: トンネル起動

```bash
# Django開発サーバー用（ポート8000）
ngrok http 8000
```

**出力例:**
```
ngrok

Session Status                online
Account                       your-email@example.com (Plan: Free)
Version                       3.5.0
Region                        Japan (jp)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### ステップ6: URL確認

1. **ngrokコンソールで確認**
   - `Forwarding` の行にHTTPS URLが表示されます
   - 例: `https://abc123.ngrok-free.app`

2. **Web UIで確認**
   - ブラウザで http://127.0.0.1:4040 にアクセス
   - リクエスト履歴、リプレイ機能などが利用可能

### ステップ7: .envファイル更新

```env
# .env
TELEGRAM_WEBHOOK_URL=https://abc123.ngrok-free.app
```

### ステップ8: Webhook設定

```bash
python manage.py set_telegram_webhook
```

---

## ⚠️ ngrok使用時の注意点

### 1. URL変更問題

**無料プランでは、ngrok再起動のたびにURLが変更されます。**

```
# 1回目の起動
https://abc123.ngrok-free.app

# ngrok再起動後
https://xyz789.ngrok-free.app  ← 変わる！
```

**対応が必要:**
- ✅ `.env`ファイルのURL更新
- ✅ Webhook再設定
- ✅ QRコード再生成（URLが埋め込まれている場合）

**自動化スクリプト例:**
```bash
# update_ngrok.bat
@echo off
echo 新しいngrok URLを入力してください:
set /p NGROK_URL=

echo TELEGRAM_WEBHOOK_URL=%NGROK_URL% > .env.temp
type .env.temp >> .env
del .env.temp

python manage.py set_telegram_webhook
echo ✅ Webhook更新完了
pause
```

### 2. 無料プランの制限

- ✅ 同時トンネル: 1つまで
- ✅ リクエスト数: 月40,000まで
- ✅ 帯域幅: 1GB/月
- ❌ カスタムドメイン不可
- ❌ URL固定不可

### 3. セキュリティ

**Authtokenは秘密情報です！**
- ❌ Gitにコミットしない
- ❌ 公開リポジトリに含めない
- ✅ ローカル設定のみで管理

### 4. パフォーマンス

ngrokを経由するため、若干のレイテンシがあります：
- 通常: 50-200ms程度の遅延
- 開発・テスト用途では問題なし
- 本番環境では直接HTTPS接続を推奨

---

## 🔄 代替手段

### 有料プランのngrok

**月$8 (Personal Plan):**
- ✅ カスタム固定サブドメイン（例: `myapp.ngrok.app`）
- ✅ 同時トンネル3つ
- ✅ リクエスト無制限
- ✅ より高速

### localtunnel (無料)

```bash
npm install -g localtunnel
lt --port 8000 --subdomain myorderapp
```

**特徴:**
- ✅ 完全無料
- ✅ サブドメイン指定可能（早い者勝ち）
- ❌ 安定性がngrokより劣る

### Cloudflare Tunnel (無料・推奨)

```bash
# インストール
# https://developers.cloudflare.com/cloudflare-one/

# トンネル作成
cloudflared tunnel create order-system

# 起動
cloudflared tunnel --url http://localhost:8000
```

**特徴:**
- ✅ 完全無料
- ✅ 固定URL
- ✅ Cloudflareの高速CDN
- ✅ DDoS保護
- ❌ 初期設定がやや複雑

---

## 🚀 本番環境への移行

**本番環境ではngrokは不要です！**

代わりに以下を使用：

### クラウドホスティング

1. **Heroku**
   ```
   https://myapp.herokuapp.com
   ```
   - 自動HTTPS対応
   - 無料プランあり

2. **AWS (Elastic Beanstalk / EC2)**
   ```
   https://myapp.us-east-1.elasticbeanstalk.com
   ```
   - Route53でカスタムドメイン
   - ALBでHTTPS終端

3. **Google Cloud (App Engine / Cloud Run)**
   ```
   https://myapp.appspot.com
   ```
   - 自動HTTPS対応

4. **Railway / Render**
   ```
   https://myapp.onrender.com
   ```
   - 無料プランでHTTPS対応

### SSL証明書

**Let's Encrypt（無料）:**
```bash
# Certbotでインストール
sudo certbot --nginx -d yourdomain.com
```

**本番環境の構成:**
```
Telegram Server
  ↓ HTTPS
Your Domain (yourdomain.com)
  ↓ HTTPS (Let's Encrypt)
Nginx / Load Balancer
  ↓ HTTP
Django (Gunicorn)
  ↓
PostgreSQL
```

---

## 📊 まとめ

### ngrokの使用箇所

| 用途 | URL例 | 説明 |
|------|------|------|
| **Telegram Webhook** | `https://abc123.ngrok-free.app/telegram/webhook/` | Botメッセージ受信 |
| **Mini Apps** | `https://abc123.ngrok-free.app/miniapp/?table_id=1` | 注文画面表示 |
| **QRコード** | `https://t.me/bot?start=table-A-1` | テーブル情報埋め込み |
| **メディア配信** | `https://abc123.ngrok-free.app/media/...` | 画像・QRコード |
| **管理画面** | `https://abc123.ngrok-free.app/admin/` | スタッフ用（オプション） |

### 登録要件

✅ **必須:**
- ngrokアカウント（無料）
- Authtoken設定

❌ **不要:**
- クレジットカード（無料プラン）
- ドメイン購入
- サーバーレンタル

### 開発フロー

```
1. ngrokインストール・設定
   ↓
2. ngrok起動 (ngrok http 8000)
   ↓
3. URLを.envに設定
   ↓
4. Django開発サーバー起動
   ↓
5. Webhook設定
   ↓
6. テスト開始
```

---

**作成日**: 2024-11-28  
**対象**: テスト環境  
**バージョン**: 1.0
