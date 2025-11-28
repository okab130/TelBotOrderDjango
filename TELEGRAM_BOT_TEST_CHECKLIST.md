# Telegram Bot テストチェックリスト

## 📋 環境セットアップ確認

### 前提条件チェック

- [ ] Python 3.10以上がインストールされている
- [ ] Djangoプロジェクトが正常に動作している
- [ ] Telegramアカウントを持っている
- [ ] インターネット接続が安定している

### パッケージインストール確認

```bash
pip list | findstr "telegram\|qrcode\|pillow\|dotenv"
```

期待される出力:
```
pillow                    10.1.0
python-dotenv             1.0.0
python-telegram-bot       20.7
qrcode                    7.4.2
```

- [ ] 上記4つのパッケージがインストールされている

### .env ファイル確認

- [ ] `.env` ファイルが存在する
- [ ] `TELEGRAM_BOT_TOKEN` が設定されている
- [ ] `TELEGRAM_BOT_USERNAME` が設定されている
- [ ] `TELEGRAM_WEBHOOK_URL` が設定されている (ngrok起動後)

### データベース確認

```bash
python manage.py showmigrations telegram_bot
```

- [ ] telegram_bot のマイグレーションが適用されている

---

## 🤖 Telegram Bot セットアップ確認

### BotFather設定チェック

- [ ] BotFatherで新しいBotを作成した
- [ ] Bot Tokenを取得した
- [ ] Botのユーザー名を設定した（`@your_bot_name`）
- [ ] Botの説明文を設定した（/setdescription）
- [ ] Menu Buttonを設定した（/setmenubutton）

### Bot情報確認

```bash
python manage.py shell
```

```python
from telegram_bot.bot import get_bot
bot = get_bot()
print(f"Bot ID: {bot.id}")
print(f"Bot Name: {bot.first_name}")
print(f"Bot Username: @{bot.username}")
```

- [ ] Bot情報が正しく取得できる

---

## 🌐 ngrok セットアップ確認

### ngrok インストール確認

```bash
ngrok version
```

- [ ] ngrokがインストールされている

### ngrok認証確認

```bash
ngrok config check
```

- [ ] Authtokenが設定されている

### ngrokトンネル起動

```bash
ngrok http 8000
```

- [ ] HTTPSのForwarding URLが表示される
- [ ] Status が "online" になっている

### ngrok Dashboard確認

ブラウザで `http://127.0.0.1:4040` を開く

- [ ] ngrok Web Interfaceが表示される
- [ ] Tunnelsタブでトンネル情報が確認できる

---

## 🔗 Webhook セットアップ確認

### Webhook設定

```bash
python manage.py set_telegram_webhook
```

期待される出力:
```
✅ Webhook設定成功: https://your-ngrok-url.ngrok-free.app/telegram/webhook/
```

- [ ] Webhookが正常に設定された

### Webhook情報確認

```bash
python manage.py check_telegram_webhook
```

または:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

確認項目:
- [ ] `url` フィールドにWebhook URLが設定されている
- [ ] `has_custom_certificate` が `false`
- [ ] `pending_update_count` が `0` または小さい数値
- [ ] `last_error_date` が存在しない、または古い

---

## 🧪 基本機能テスト

### テスト1: Bot起動テスト

1. Telegramアプリを開く
2. 作成したBotを検索
3. `/start` コマンドを送信

期待される動作:
- [ ] ウェルカムメッセージが返ってくる
- [ ] メッセージにBot名が含まれる

### テスト2: ログ確認

Djangoサーバーのターミナルを確認:

```
[日時] "POST /telegram/webhook/ HTTP/1.1" 200
```

- [ ] Webhook経由でリクエストが届いている

ngrok Dashboardを確認 (`http://127.0.0.1:4040`):

- [ ] POST リクエストが記録されている
- [ ] ステータスコードが 200

### テスト3: データベース確認

```bash
python manage.py shell
```

```python
from telegram_bot.models import TelegramUser, TelegramMessage
print(f"ユーザー数: {TelegramUser.objects.count()}")
print(f"メッセージ数: {TelegramMessage.objects.count()}")

# 最新のユーザー
user = TelegramUser.objects.first()
if user:
    print(f"最新ユーザー: {user.get_display_name()}")
```

- [ ] TelegramUserが作成されている
- [ ] TelegramMessageが記録されている

---

## 📍 QRコード・セッション機能テスト

### テスト4: QRコード生成

```bash
python manage.py generate_qr_codes
```

- [ ] QRコードが生成される
- [ ] `media/qr_codes/` ディレクトリにPNGファイルが作成される

### テスト5: テーブルQRコードスキャン

1. 管理画面 (`http://localhost:8000/admin/`) にログイン
2. テーブル管理を開く
3. QRコードリンクをクリック
4. QRコードをTelegramでスキャン、または `/start table-A-1` コマンドを送信

期待される動作:
- [ ] 人数選択画面が表示される
- [ ] ボタンが1〜10名分表示される

### テスト6: セッション作成

1. 人数（例: 4名）を選択
2. メインメニューが表示されることを確認

期待される動作:
- [ ] セッションコードが表示される
- [ ] テーブル番号が表示される
- [ ] メインメニューボタンが表示される

データベース確認:
```python
from orders.models import Session
session = Session.objects.last()
print(f"セッションコード: {session.session_code}")
print(f"テーブル: {session.table.table_number}")
print(f"人数: {session.party_size}")
```

- [ ] Sessionレコードが作成されている

---

## 🍽️ 注文機能テスト

### テスト7: メニュー表示

1. 「📋 メニューを見る」ボタンをタップ
2. カテゴリを選択
3. メニュー項目を選択

期待される動作:
- [ ] カテゴリ一覧が表示される
- [ ] メニュー項目一覧が表示される
- [ ] 価格が正しく表示される
- [ ] 売り切れ商品に ❌ マークが付いている

### テスト8: カートに追加

1. メニュー項目を選択
2. 数量を選択（例: 2個）
3. カートに追加

期待される動作:
- [ ] 「カートに追加しました」というメッセージが表示される
- [ ] カート画面に遷移する
- [ ] 商品名、数量、小計が表示される

### テスト9: 注文確定

1. 「✅ 注文確定」ボタンをタップ

期待される動作:
- [ ] 注文番号が表示される
- [ ] 合計金額が表示される
- [ ] カートがクリアされる

データベース確認:
```python
from orders.models import Order, OrderItem
order = Order.objects.last()
print(f"注文番号: {order.order_number}")
print(f"合計金額: {order.total_amount}")
print(f"明細数: {order.items.count()}")
```

- [ ] Orderレコードが作成されている
- [ ] OrderItemレコードが作成されている

### テスト10: 管理画面での注文確認

1. 管理画面の「注文管理」を開く
2. 最新の注文を確認

期待される動作:
- [ ] Botから作成した注文が表示される
- [ ] ステータスが「未調理」
- [ ] Telegram ユーザー名が表示される

---

## 🔔 店員呼び出し機能テスト

### テスト11: 店員呼び出し

1. メインメニューで「🔔 店員を呼ぶ」をタップ
2. 理由を選択（例: 💧 お水）

期待される動作:
- [ ] 理由選択画面が表示される
- [ ] 「呼び出しました」というメッセージが表示される

データベース確認:
```python
from orders.models import StaffCall
call = StaffCall.objects.last()
print(f"理由: {call.reason}")
print(f"ステータス: {call.status}")
```

- [ ] StaffCallレコードが作成されている

### テスト12: 管理画面での呼び出し確認

1. 管理画面の「店員呼び出し管理」を開く

期待される動作:
- [ ] 呼び出しが表示される
- [ ] ステータスが「未対応」
- [ ] テーブル番号が表示される

---

## 💰 会計機能テスト

### テスト13: 会計依頼

1. メインメニューで「💰 会計」をタップ
2. 合計金額を確認
3. 「会計依頼」ボタンをタップ

期待される動作:
- [ ] 注文数が表示される
- [ ] 合計金額が表示される
- [ ] 「リクエストしました」というメッセージが表示される

データベース確認:
```python
from orders.models import Payment
payment = Payment.objects.last()
print(f"金額: {payment.total_amount}")
print(f"ステータス: {payment.status}")
```

- [ ] Paymentレコードが作成されている

### テスト14: 管理画面での会計処理

1. 管理画面の「会計管理」を開く
2. 最新の会計依頼を選択
3. 「会計完了」アクションを実行
4. 支払い方法を選択（例: 現金）

期待される動作:
- [ ] ステータスが「完了」に変更される
- [ ] 支払い方法が記録される
- [ ] 完了日時が記録される

---

## 🔄 エラーハンドリングテスト

### テスト15: 売り切れ商品の注文

1. 管理画面で商品を売り切れに設定
2. Botでその商品を選択

期待される動作:
- [ ] 「❌ 売り切れ」と表示される
- [ ] カートに追加できない

### テスト16: セッションなしで注文

1. 新しいチャットを開始（セッションなし）
2. メニューを見ようとする

期待される動作:
- [ ] エラーメッセージが表示される
- [ ] または、セッション作成を促される

### テスト17: ネットワークエラー

1. ngrokを停止
2. Botでコマンドを送信

期待される動作:
- [ ] Telegramで送信マークが表示される
- [ ] タイムアウト後にエラーが表示される

ngrok再起動後:
- [ ] Webhookを再設定できる

---

## 📊 パフォーマンステスト

### テスト18: 複数ユーザー同時アクセス

1. 複数のTelegramアカウント（または友人）でBotにアクセス
2. 同時に注文を作成

期待される動作:
- [ ] それぞれのセッションが独立している
- [ ] 注文が混在しない
- [ ] レスポンスが遅延しない

### テスト19: 大量メニュー表示

1. 管理画面で50個以上のメニューを作成
2. Botでメニューを表示

期待される動作:
- [ ] すべてのメニューが表示される
- [ ] ボタンが多すぎる場合でも崩れない
- [ ] スクロール可能

---

## 🔒 セキュリティテスト

### テスト20: 不正なWebhookリクエスト

```bash
curl -X POST http://localhost:8000/telegram/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
```

期待される動作:
- [ ] エラーが適切に処理される
- [ ] サーバーがクラッシュしない

### テスト21: Bot Token漏洩チェック

1. コードベースで "TELEGRAM_BOT_TOKEN" を検索
2. .envファイルが.gitignoreに含まれているか確認

- [ ] Bot Tokenがハードコードされていない
- [ ] .envが.gitignoreに含まれている

---

## 📝 ログ・監視テスト

### テスト22: エラーログ確認

Djangoサーバーのログを確認:

- [ ] 正常なリクエストが記録されている
- [ ] エラーが適切にログされている

### テスト23: ngrok リクエストログ

ngrok Dashboard (`http://127.0.0.1:4040`) を確認:

- [ ] すべてのWebhookリクエストが記録されている
- [ ] リクエスト/レスポンスの詳細が確認できる
- [ ] エラーリクエストが特定できる

---

## 🎯 統合テスト（エンドツーエンド）

### テスト24: フルフロー

1. QRコードスキャン（セッション作成）
2. メニュー閲覧
3. カートに追加
4. 注文確定
5. 追加注文
6. 店員呼び出し
7. 会計依頼
8. 管理画面で会計完了
9. セッション終了

各ステップで:
- [ ] 正常に動作する
- [ ] データベースに正しく記録される
- [ ] ユーザーに適切なフィードバックがある

---

## ✅ 最終チェック

### デプロイ前確認

- [ ] すべての必須機能が動作する
- [ ] エラーハンドリングが適切
- [ ] セキュリティ対策が実施されている
- [ ] パフォーマンスが許容範囲内
- [ ] ログが適切に記録されている

### ドキュメント確認

- [ ] README.mdが更新されている
- [ ] API_IMPLEMENTATION.mdが最新
- [ ] TELEGRAM_BOT_SETUP.mdが完全
- [ ] 環境変数のドキュメントがある

---

## 🐛 トラブルシューティング

問題が発生した場合は、`TELEGRAM_BOT_SETUP.md` の「トラブルシューティング」セクションを参照してください。

---

**テスト完了日**: ________________  
**テスト実施者**: ________________  
**合格/不合格**: ________________

**備考**:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
