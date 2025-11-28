# Telegram Bot実装ガイド

## 📋 このドキュメントについて

このドキュメントでは、Telegram Botの詳細な実装手順とコードを提供します。
`TELEGRAM_BOT_SETUP.md` で環境セットアップを完了してから、このガイドに従って実装を進めてください。

---

## 実装手順

### ステップ1: telegram_botアプリを作成

```bash
python manage.py startapp telegram_bot
```

### ステップ2: settings.pyに追加

`mobile_order_system/settings.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

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

### ステップ3: 実装ファイルを作成

以下のコマンドを順番に実行してください：

```bash
# プロジェクトルートで実行
cd C:\Users\user\gh\TelBotOrderDjango

# 1. models.py を実装
# 2. bot.py を作成
# 3. keyboards.py を作成
# 4. handlers.py を作成
# 5. views.py を作成
# 6. urls.py を作成
# 7. utils.py を作成
# 8. management commands を作成
```

---

## コード実装

### 実装済みファイル一覧

次のステップで、以下のファイルを作成します：

1. ✅ `telegram_bot/models.py` - TelegramUser, TelegramMessage
2. ✅ `telegram_bot/bot.py` - Bot初期化と基本関数
3. ✅ `telegram_bot/keyboards.py` - インラインキーボード定義
4. ✅ `telegram_bot/handlers.py` - コマンド・コールバックハンドラー
5. ⏳ `telegram_bot/views.py` - Webhook受信エンドポイント
6. ⏳ `telegram_bot/urls.py` - URLルーティング
7. ⏳ `telegram_bot/utils.py` - ユーティリティ関数
8. ⏳ Management Commands

---

## 次のコマンド

実装を開始するために、以下のコマンドを実行してください：

```bash
# telegram_botアプリを作成
python manage.py startapp telegram_bot

# マイグレーション作成
python manage.py makemigrations telegram_bot

# マイグレーション適用
python manage.py migrate

# 管理画面にモデル登録確認
python manage.py shell
>>> from telegram_bot.models import TelegramUser
>>> TelegramUser.objects.count()
```

---

## テスト用コマンド

```bash
# Webhook設定
python manage.py set_telegram_webhook

# Webhook情報確認
python manage.py check_telegram_webhook

# QRコード生成
python manage.py generate_qr_codes
```

---

**次のドキュメント**: 残りのファイル実装（views.py, urls.py等）を作成します。

準備ができたら、「実装を続けてください」と指示してください。
