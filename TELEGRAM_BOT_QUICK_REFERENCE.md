# Telegram Bot クイックリファレンス

## 🚀 クイックスタート（5分セットアップ）

### 1. セットアップスクリプト実行
```bash
setup_telegram_bot.bat
```

### 2. .env ファイル編集
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # BotFatherから取得
TELEGRAM_BOT_USERNAME=your_restaurant_order_bot
```

### 3. 開発環境起動
```bash
start_dev.bat
```

### 4. Webhook設定
```bash
# ngrokのURLを.envに設定してから実行
python manage.py set_telegram_webhook
```

### 5. Botをテスト
Telegramで `/start` コマンドを送信

---

## 📋 よく使うコマンド

### 開発サーバー
```bash
# 起動
python manage.py runserver 0.0.0.0:8000

# バックグラウンド起動（Windows）
start /B python manage.py runserver 0.0.0.0:8000
```

### ngrok
```bash
# トンネル起動
ngrok http 8000

# 認証設定
ngrok config add-authtoken YOUR_AUTHTOKEN

# バージョン確認
ngrok version
```

### Webhook管理
```bash
# Webhook設定
python manage.py set_telegram_webhook

# Webhook削除
python manage.py delete_telegram_webhook

# Webhook情報確認
python manage.py check_telegram_webhook
```

### QRコード
```bash
# 全テーブルのQRコード生成
python manage.py generate_qr_codes

# 特定テーブルのみ
python manage.py generate_qr_codes --table A-1
```

### データベース
```bash
# マイグレーション作成
python manage.py makemigrations telegram_bot

# マイグレーション適用
python manage.py migrate

# データベースリセット
rm db.sqlite3
python manage.py migrate
python manage.py create_test_data
```

### テスト
```bash
# 全テスト実行
python manage.py test

# telegram_botアプリのみ
python manage.py test telegram_bot

# 詳細表示
python manage.py test --verbosity=2
```

---

## 🔧 トラブルシューティング クイックフィックス

### Botが応答しない
```bash
# 1. Webhook情報確認
python manage.py check_telegram_webhook

# 2. Webhook削除・再設定
python manage.py delete_telegram_webhook
python manage.py set_telegram_webhook

# 3. ngrok再起動
# ngrokウィンドウで Ctrl+C
ngrok http 8000
# 新しいURLを.envに設定
```

### データベースエラー
```bash
# マイグレーションリセット
python manage.py migrate telegram_bot zero
python manage.py migrate telegram_bot
```

### ngrok URLが変わった
```bash
# 1. 新しいURLを.envに反映
notepad .env

# 2. Webhook再設定
python manage.py set_telegram_webhook
```

### メディアファイルが見つからない
```bash
# media ディレクトリ作成
mkdir media
mkdir media\qr_codes

# QRコード再生成
python manage.py generate_qr_codes
```

---

## 💡 便利なコマンド

### Bot情報確認
```bash
python manage.py shell
```
```python
from telegram_bot.bot import get_bot
bot = get_bot()
print(f"Bot: @{bot.username} (ID: {bot.id})")
```

### 統計情報確認
```python
from telegram_bot.models import TelegramUser
from orders.models import Order, Session

print(f"総ユーザー数: {TelegramUser.objects.count()}")
print(f"総注文数: {Order.objects.count()}")
print(f"アクティブセッション: {Session.objects.filter(status='active').count()}")
```

### 最近のアクティビティ
```python
from telegram_bot.models import TelegramMessage
from django.utils import timezone
from datetime import timedelta

recent = timezone.now() - timedelta(hours=1)
messages = TelegramMessage.objects.filter(created_at__gte=recent)
print(f"過去1時間のメッセージ数: {messages.count()}")
```

---

## 🌐 URL一覧

### ローカル開発
- Django Admin: http://localhost:8000/admin/
- REST API: http://localhost:8000/api/
- Webhook: http://localhost:8000/telegram/webhook/
- ngrok Dashboard: http://127.0.0.1:4040

### 本番環境（例）
- サイト: https://your-domain.com/
- Admin: https://your-domain.com/admin/
- API: https://your-domain.com/api/
- Webhook: https://your-domain.com/telegram/webhook/

---

## 📱 Telegram Bot コマンド

### ユーザーコマンド
- `/start` - Bot開始
- `/start table-A-1` - テーブルA-1のセッション開始
- `/help` - ヘルプ表示
- `/menu` - メニュー表示

### 管理者コマンド（予定）
- `/admin` - 管理ダッシュボード
- `/stats` - 統計情報
- `/broadcast` - 一斉送信

---

## 🔑 環境変数リファレンス

### 必須
```env
TELEGRAM_BOT_TOKEN=      # BotFatherから取得
TELEGRAM_BOT_USERNAME=   # Botのユーザー名
TELEGRAM_WEBHOOK_URL=    # ngrokまたは本番URL
SECRET_KEY=              # Django SECRET_KEY
```

### オプション
```env
DEBUG=True                              # デバッグモード
ALLOWED_HOSTS=localhost,127.0.0.1       # 許可ホスト
DATABASE_URL=sqlite:///db.sqlite3       # データベースURL
TIME_ZONE=Asia/Tokyo                    # タイムゾーン
LANGUAGE_CODE=ja                        # 言語コード
```

---

## 📊 ステータスコード

### セッション
- `active` - アクティブ
- `calling_staff` - 店員呼び出し中
- `payment_requested` - 会計依頼中
- `completed` - 完了

### 注文
- `pending` - 未調理
- `cooking` - 調理中
- `ready` - 完了
- `served` - 提供済み
- `cancelled` - キャンセル

### 店員呼び出し
- `pending` - 未対応
- `responding` - 対応中
- `resolved` - 解決済み

### 会計
- `pending` - 未会計
- `paid` - 支払い済み
- `cancelled` - キャンセル

---

## 🎨 インラインキーボードアイコン

### 使用可能な絵文字
- 📋 メニュー
- 🛒 カート
- 📦 注文
- 🔔 店員呼び出し
- 💰 会計
- 🏠 ホーム
- 🔙 戻る
- ✅ 確認
- ❌ キャンセル
- 💧 お水
- 🍴 食器
- ❓ 質問
- 📝 その他

---

## 🔐 セキュリティチェックリスト

- [ ] .env ファイルが .gitignore に含まれる
- [ ] Bot Token がコードにハードコードされていない
- [ ] 本番環境で DEBUG=False
- [ ] ALLOWED_HOSTS が適切に設定
- [ ] HTTPS Webhookのみ使用
- [ ] 定期的な依存パッケージ更新

---

## 📚 関連ドキュメント

### プロジェクト内
- `TELEGRAM_BOT_SETUP.md` - 詳細セットアップガイド
- `TELEGRAM_BOT_IMPLEMENTATION.md` - 実装ガイド
- `TELEGRAM_BOT_TEST_CHECKLIST.md` - テストチェックリスト
- `API_IMPLEMENTATION.md` - REST API仕様
- `README.md` - プロジェクト概要

### 外部リンク
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [ngrok Documentation](https://ngrok.com/docs)

---

## 🆘 サポート

### 問題が解決しない場合

1. **ログを確認**
   - Djangoサーバーのコンソール出力
   - ngrok Dashboard (http://127.0.0.1:4040)
   - ブラウザの開発者ツール

2. **Webhook状態を確認**
   ```bash
   python manage.py check_telegram_webhook
   ```

3. **データベースを確認**
   ```bash
   python manage.py shell
   # TelegramUser, TelegramMessage, Session等を確認
   ```

4. **設定ファイルを確認**
   - `.env` ファイル
   - `settings.py` の INSTALLED_APPS
   - `urls.py` のルーティング

5. **クリーンインストール**
   ```bash
   # 仮想環境を再作成
   deactivate
   rm -rf venv
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## 📞 緊急時の対処

### サーバーがクラッシュした
```bash
# プロセス確認
tasklist | findstr python

# プロセス強制終了
taskkill /F /IM python.exe

# 再起動
python manage.py runserver 0.0.0.0:8000
```

### Webhookが動作しない
```bash
# Webhook完全リセット
curl https://api.telegram.org/bot<TOKEN>/deleteWebhook
python manage.py set_telegram_webhook --force
```

### データが壊れた
```bash
# バックアップから復元（事前にバックアップしておく）
copy db.sqlite3.backup db.sqlite3

# または新規作成
rm db.sqlite3
python manage.py migrate
python manage.py create_test_data
```

---

**最終更新**: 2024-11-28  
**バージョン**: 1.0  
**対象環境**: 開発・テスト環境
