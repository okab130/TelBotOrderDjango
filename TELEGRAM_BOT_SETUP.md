# Telegram Bot テスト環境セットアップガイド

## 📋 目次
1. [前提条件](#前提条件)
2. [Telegram Bot作成](#telegram-bot作成)
3. [開発環境セットアップ](#開発環境セットアップ)
4. [ローカルテストトンネル設定](#ローカルテストトンネル設定)
5. [Telegram Bot実装](#telegram-bot実装)
6. [テスト手順](#テスト手順)
7. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必要なもの
- ✅ Telegram アカウント
- ✅ Python 3.10以上
- ✅ 現在のDjangoプロジェクト（実装済み）
- ✅ インターネット接続

### システム要件
- Windows 10/11 または macOS/Linux
- 最低2GB RAM
- 500MB以上のディスク空き容量

---

## Telegram Bot作成

### ステップ1: BotFatherでBot作成

1. **Telegramアプリを開く**

2. **BotFatherを検索**
   - 検索欄に `@BotFather` と入力
   - 公式の青いチェックマーク付きアカウントを選択

3. **新しいBotを作成**
   ```
   /newbot
   ```

4. **Bot名を入力**（例）
   ```
   Mobile Order System
   ```

5. **Botのユーザー名を入力**（ユニークである必要があります）
   ```
   your_restaurant_order_bot
   ```
   ※ 名前は `bot` で終わる必要があります

6. **Bot Tokenを保存**
   - BotFatherから受け取ったトークンをコピー
   - 形式: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
   - ⚠️ **このトークンは絶対に公開しないこと！**

### ステップ2: Bot設定

1. **Mini Appsを有効化**
   ```
   /setmenubutton
   ```
   - 作成したBotを選択
   - `Edit Menu Button` を選択
   - ボタン名: `注文する`
   - URL: `https://your-domain.com/` （後で変更）

2. **Botの説明を設定**
   ```
   /setdescription
   ```
   - Botを選択
   - 説明を入力:
   ```
   飲食店のテーブルオーダーシステムです。
   QRコードをスキャンして、簡単に注文できます。
   ```

3. **Botのプロフィール画像を設定**（オプション）
   ```
   /setuserpic
   ```

### ステップ3: テストグループ作成

1. **新規グループを作成**
   - グループ名: `注文システムテスト`
   
2. **Botをグループに追加**
   - 作成したBotを検索して追加

3. **Botを管理者に設定**（オプション）
   - グループ設定 → 管理者 → Botを追加

---

## 開発環境セットアップ

### ステップ1: 必要なパッケージをインストール

```bash
cd C:\Users\user\gh\TelBotOrderDjango

# 依存パッケージをインストール
pip install python-telegram-bot==20.7
pip install qrcode==7.4.2
pip install pillow==10.1.0
pip install python-dotenv==1.0.0
```

### ステップ2: requirements.txtを更新

```bash
# 現在のパッケージをエクスポート
pip freeze > requirements.txt
```

### ステップ3: 環境変数ファイル作成

プロジェクトルートに `.env` ファイルを作成：

```bash
# .envファイルを作成
New-Item -Path .env -ItemType File
```

`.env` の内容:
```env
# Django設定
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*.ngrok-free.app

# Telegram Bot設定
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=your_restaurant_order_bot

# Webhook URL（ngrok起動後に更新）
TELEGRAM_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app

# データベース
DATABASE_URL=sqlite:///db.sqlite3

# その他
TIME_ZONE=Asia/Tokyo
LANGUAGE_CODE=ja
```

### ステップ4: .gitignoreに追加

`.gitignore` に以下を追加（既に含まれていない場合）:
```
.env
*.log
db.sqlite3
__pycache__/
*.pyc
media/
staticfiles/
```

---

## ローカルテストトンネル設定

Telegram Webhookはパブリックなhttps URLが必要なため、ローカル開発にはトンネルツールを使用します。

### オプション1: ngrok（推奨）

#### インストール

1. **ngrokをダウンロード**
   - https://ngrok.com/download
   - Windows版をダウンロード

2. **ngrokを配置**
   ```bash
   # ダウンロードしたngrok.exeをプロジェクトフォルダに配置
   # または、PATHに追加
   ```

3. **ngrokアカウント作成**（無料）
   - https://dashboard.ngrok.com/signup
   - 登録後、Authtokenを取得

4. **Authtokenを設定**
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

#### 使用方法

```bash
# Djangoサーバー用トンネルを起動
ngrok http 8000
```

出力例:
```
Session Status                online
Account                       your-email@example.com
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000
```

⚠️ **この `https://abc123.ngrok-free.app` URLを `.env` ファイルの `TELEGRAM_WEBHOOK_URL` に設定**

### オプション2: localtunnel

```bash
# インストール
npm install -g localtunnel

# 使用
lt --port 8000 --subdomain your-order-system
```

### オプション3: Cloudflare Tunnel（無料、永続的URL）

```bash
# インストール
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# 使用
cloudflared tunnel --url http://localhost:8000
```

---

## Telegram Bot実装

### ステップ1: Botアプリケーション作成

```bash
# 新しいDjangoアプリを作成
python manage.py startapp telegram_bot
```

### ステップ2: settings.pyを更新

`mobile_order_system/settings.py` に追加:

```python
import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# INSTALLED_APPSに追加
INSTALLED_APPS = [
    # ... 既存のアプリ
    'telegram_bot',
]

# Telegram Bot設定
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')

# ALLOWED_HOSTSを更新
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

### ステップ3: URLルーティング設定

`mobile_order_system/urls.py` に追加:

```python
from django.urls import path, include

urlpatterns = [
    # ... 既存のURL
    path('telegram/', include('telegram_bot.urls')),
]
```

### ステップ4: Telegram Bot実装ファイルを作成

以下のファイルを作成します：

1. **telegram_bot/bot.py** - Bot本体
2. **telegram_bot/handlers.py** - コマンドハンドラー
3. **telegram_bot/views.py** - Webhook受信
4. **telegram_bot/urls.py** - URLルーティング
5. **telegram_bot/utils.py** - ユーティリティ関数

詳細な実装は次のセクションで提供します。

---

## テスト手順

### テスト環境の起動

#### ターミナル1: Djangoサーバー起動

```bash
cd C:\Users\user\gh\TelBotOrderDjango
python manage.py runserver 0.0.0.0:8000
```

#### ターミナル2: ngrokトンネル起動

```bash
ngrok http 8000
```

ngrokが表示するHTTPS URLをコピー（例: `https://abc123.ngrok-free.app`）

#### ターミナル3: Webhook設定

```bash
# .envファイルのTELEGRAM_WEBHOOK_URLを更新してから実行
python manage.py set_telegram_webhook
```

または、curlで直接設定:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://abc123.ngrok-free.app/telegram/webhook/"
```

### テストシナリオ

#### 1. Bot起動テスト

1. Telegramで自分のBotを検索
2. `/start` コマンドを送信
3. ウェルカムメッセージが返ってくることを確認

#### 2. QRコード生成テスト

1. 管理画面でテーブルを作成
2. QRコードが生成されることを確認
3. QRコードをダウンロード

#### 3. セッション開始テスト

1. BotのチャットでQRコードをスキャン（または `/start table-A-1` コマンド）
2. 人数選択画面が表示されることを確認
3. 人数を選択
4. メニュー画面が表示されることを確認

#### 4. 注文フローテスト

1. カテゴリを選択
2. メニュー項目を選択
3. 数量を選択
4. カートに追加
5. 注文確定
6. 注文番号が表示されることを確認

#### 5. 管理画面確認テスト

1. Django Adminにログイン
2. 注文管理画面を開く
3. 新規注文が表示されることを確認
4. ステータスを「調理中」に更新
5. Telegram Botに通知が届くことを確認

#### 6. 店員呼び出しテスト

1. Bot画面で「店員を呼ぶ」ボタンをタップ
2. 理由を選択
3. メッセージを入力（オプション）
4. 送信
5. 管理画面で呼び出しが表示されることを確認

#### 7. 会計テスト

1. Bot画面で「会計」ボタンをタップ
2. 合計金額が表示されることを確認
3. 会計依頼が送信される
4. 管理画面で会計依頼が表示されることを確認
5. 管理画面で会計完了処理
6. Botに完了通知が届くことを確認

### ログ確認

```bash
# Djangoサーバーのログ
# ターミナル1で確認

# ngrokのリクエストログ
# http://127.0.0.1:4040 をブラウザで開く
```

---

## トラブルシューティング

### 問題1: Webhookが設定できない

**症状**: `setWebhook` が失敗する

**解決策**:
```bash
# 現在のWebhook情報を確認
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo

# Webhookを削除
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook

# 再設定
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-ngrok-url.ngrok-free.app/telegram/webhook/"
```

### 問題2: Botが応答しない

**確認事項**:
1. ✅ ngrokが起動しているか
2. ✅ Djangoサーバーが起動しているか
3. ✅ `.env` のBot Tokenが正しいか
4. ✅ Webhook URLが正しいか
5. ✅ ngrokのログでリクエストが届いているか (`http://127.0.0.1:4040`)

**デバッグ方法**:
```bash
# Webhook情報を確認
python manage.py shell

from telegram_bot.bot import bot
print(bot.get_webhook_info())
```

### 問題3: HTTPS証明書エラー

**症状**: SSL/TLS関連のエラー

**解決策**:
```python
# settings.py に追加
SECURE_SSL_REDIRECT = False  # 開発環境のみ
```

### 問題4: ngrokのURLが変わる

**症状**: ngrok再起動のたびにURLが変わり、Webhook再設定が必要

**解決策**:
1. ngrokの有料プラン（月$8）で固定サブドメインを使用
2. または、Cloudflare Tunnelを使用（無料で永続的URL）

**Cloudflare Tunnel設定**:
```bash
# インストール
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# トンネル作成
cloudflared tunnel create order-system

# トンネル起動
cloudflared tunnel --url http://localhost:8000
```

### 問題5: データベースエラー

**症状**: IntegrityError や DoesNotExist エラー

**解決策**:
```bash
# マイグレーション再実行
python manage.py migrate

# テストデータ再作成
python manage.py create_test_data

# データベースリセット（注意: 全データ削除）
rm db.sqlite3
python manage.py migrate
python manage.py create_test_data
```

### 問題6: メディアファイルが表示されない

**症状**: メニュー画像やQRコードが表示されない

**解決策**:
```python
# settings.py を確認
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

```python
# urls.py に追加（開発環境のみ）
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 問題7: Telegram APIレート制限

**症状**: `429 Too Many Requests` エラー

**解決策**:
```python
# bot.py でレート制限を実装
import time
from functools import wraps

def rate_limit(seconds=1):
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < seconds:
                time.sleep(seconds - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

---

## テスト用コマンド一覧

### Telegram Bot管理コマンド

```bash
# Webhook設定
python manage.py set_telegram_webhook

# Webhook削除
python manage.py delete_telegram_webhook

# Webhook情報確認
python manage.py check_telegram_webhook

# QRコード生成（全テーブル）
python manage.py generate_qr_codes

# Bot情報確認
python manage.py shell
>>> from telegram_bot.bot import bot
>>> print(bot.get_me())
```

### APIテスト（curl）

```bash
# メニュー取得
curl http://localhost:8000/api/menu-items/

# セッション作成
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{"qr_code_url":"https://t.me/yourbot?start=table-A-1","party_size":4}'

# 注文作成
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"session_code":"TBL1-20241128-ABC123","telegram_user_id":"123","items":[{"menu_item_id":1,"quantity":2}]}'
```

### 開発サーバー起動スクリプト

`start_dev.bat` (Windows) または `start_dev.sh` (Mac/Linux) を作成:

```bash
@echo off
echo Starting Mobile Order System...
echo.

echo [1/3] Starting Django Server...
start cmd /k "cd C:\Users\user\gh\TelBotOrderDjango && python manage.py runserver 0.0.0.0:8000"

timeout /t 3

echo [2/3] Starting ngrok tunnel...
start cmd /k "ngrok http 8000"

echo.
echo [3/3] Setup complete!
echo.
echo Next steps:
echo 1. Copy the ngrok HTTPS URL from the ngrok window
echo 2. Update .env file with the new TELEGRAM_WEBHOOK_URL
echo 3. Run: python manage.py set_telegram_webhook
echo.
pause
```

---

## セキュリティチェックリスト

開発環境でも以下を確認してください：

- [ ] `.env` ファイルが `.gitignore` に含まれている
- [ ] Bot Tokenがコードにハードコードされていない
- [ ] `DEBUG=False` を本番環境で設定
- [ ] `ALLOWED_HOSTS` が適切に設定されている
- [ ] セキュアなSECRET_KEYを使用
- [ ] Webhook URLがHTTPSである
- [ ] データベースバックアップ体制がある

---

## 次のステップ

1. **基本実装**: 次のドキュメント `TELEGRAM_BOT_IMPLEMENTATION.md` を参照
2. **Mini Apps UI**: Telegram Mini Apps用のReact/Vue.jsフロントエンド実装
3. **本番デプロイ**: Heroku/AWS/GCPへのデプロイ
4. **監視設定**: Sentry, New Relicなどのエラー監視

---

**作成日**: 2024-11-28  
**対象**: テスト環境  
**前提**: Django REST APIが実装済み
