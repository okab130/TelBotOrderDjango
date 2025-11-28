# テスト環境セットアップ手順書

## 📋 目次
1. [環境準備](#環境準備)
2. [依存パッケージインストール](#依存パッケージインストール)
3. [環境変数設定](#環境変数設定)
4. [データベースセットアップ](#データベースセットアップ)
5. [ngrok設定](#ngrok設定)
6. [Telegram Bot設定](#telegram-bot設定)
7. [アプリケーション起動](#アプリケーション起動)
8. [動作確認](#動作確認)
9. [トラブルシューティング](#トラブルシューティング)

---

## 環境準備

### 必要なソフトウェア
- ✅ Python 3.10以上
- ✅ pip (Pythonパッケージマネージャー)
- ✅ Git
- ✅ ngrok (ローカル開発用トンネル)
- ✅ Telegramアカウント

### システム要件
- Windows 10/11、macOS、またはLinux
- 最低2GB RAM
- 1GB以上のディスク空き容量

---

## 依存パッケージインストール

### 1. 仮想環境作成（推奨）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 依存パッケージインストール

```bash
pip install -r requirements.txt
```

インストールされるパッケージ:
- Django 5.0
- djangorestframework 3.14.0
- python-telegram-bot 21.0
- python-dotenv 1.0.0
- qrcode 7.4.2
- Pillow 10.4.0
- django-cors-headers 4.3.0

---

## 環境変数設定

### 1. .envファイル作成

プロジェクトルートに`.env`ファイルを作成:

```bash
# Windowsの場合
copy .env.example .env

# macOS/Linuxの場合
cp .env.example .env
```

### 2. .envファイル編集

`.env`ファイルを開いて以下を設定:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN=8267396699:AAEPqp5XQnf4xcHKlycTiNXEnajhzJBODmc
TELEGRAM_BOT_USERNAME=mobail_order_bot
TELEGRAM_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app
```

**重要:**
- `SECRET_KEY`: 本番環境では必ず変更してください
- `TELEGRAM_BOT_TOKEN`: 提供されたBotトークンを使用
- `TELEGRAM_WEBHOOK_URL`: ngrok起動後に更新します（後述）

---

## データベースセットアップ

### 1. マイグレーション実行

```bash
python manage.py migrate
```

実行されるマイグレーション:
- Store（店舗）
- Table（テーブル）
- Category（カテゴリ）
- MenuItem（メニュー項目）
- Session（セッション）
- Order（注文）
- OrderItem（注文明細）
- StaffCall（店員呼び出し）
- Payment（会計）
- User（ユーザー）

### 2. スーパーユーザー作成

```bash
python manage.py createsuperuser
```

プロンプトに従って入力:
- ユーザー名: admin
- メールアドレス: admin@example.com
- パスワード: (任意、8文字以上)

### 3. テストデータ作成

```bash
python manage.py create_test_data
```

作成されるデータ:
- ✅ 店舗: 1件（テスト店舗）
- ✅ テーブル: 5件（A-1 〜 A-5）
- ✅ カテゴリ: 4件（前菜、メイン、ドリンク、デザート）
- ✅ メニュー項目: 20件以上

---

## ngrok設定

### 1. ngrokインストール

#### Windows
1. https://ngrok.com/download からダウンロード
2. zipファイルを解凍
3. `ngrok.exe`を適当なフォルダに配置
4. 環境変数PATHに追加（オプション）

#### macOS（Homebrew使用）
```bash
brew install ngrok
```

#### Linux
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### 2. ngrokアカウント登録（無料）

1. https://dashboard.ngrok.com/signup にアクセス
2. Googleアカウントなどでサインアップ
3. Authtokenを取得

### 3. ngrok認証設定

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### 4. ngrok起動

```bash
# Django開発サーバーのポート8000をトンネル
ngrok http 8000
```

**出力例:**
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000
```

### 5. .envファイル更新

ngrokから取得したURLを`.env`に設定:

```env
TELEGRAM_WEBHOOK_URL=https://abc123.ngrok-free.app
```

**⚠️ 重要:**
- ngrokを再起動するたびにURLが変わります（無料プラン）
- URLが変わったら`.env`を更新し、Webhookを再設定してください

---

## Telegram Bot設定

### 1. QRコード生成

```bash
python manage.py generate_qrcodes
```

生成されるQRコード:
- 保存先: `media/qrcodes/`
- ファイル名: `table_{id}_{table_number}.png`

### 2. Webhook設定

```bash
python manage.py set_telegram_webhook
```

成功すると:
```
✅ Webhook設定完了
```

### 3. Webhook確認

ブラウザで以下にアクセス:
```
https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getWebhookInfo
```

`url`フィールドに正しいWebhook URLが設定されていることを確認。

---

## アプリケーション起動

### 1. 開発サーバー起動

```bash
python manage.py runserver 0.0.0.0:8000
```

**または、バッチファイル使用（Windows）:**

```bash
start_dev.bat
```

### 2. 起動確認

ブラウザで以下にアクセス:

- **管理画面**: http://localhost:8000/admin/
  - ユーザー名: admin
  - パスワード: (作成時に設定したもの)

- **API**: http://localhost:8000/api/

- **Mini Apps**: http://localhost:8000/miniapp/?table_id=1

---

## 動作確認

### 1. Telegram Botテスト

1. Telegramアプリを開く
2. `@mobail_order_bot` を検索
3. `/start` コマンド送信
4. ボットからウェルカムメッセージが返ってくることを確認

### 2. Mini Appsテスト

1. ブラウザで管理画面にアクセス: http://localhost:8000/admin/
2. Tables（テーブル）を選択
3. テーブル一覧で「qr_code_url」をコピー
4. Telegramの検索バーにURLを貼り付けてアクセス
5. Mini Appsが起動し、来店人数入力画面が表示されることを確認

### 3. 注文フローテスト

1. Mini Appsで来店人数を入力（例: 2人）
2. 「注文を開始する」ボタンをクリック
3. メニュー一覧が表示されることを確認
4. 商品を選択して注文
5. 管理画面の注文ダッシュボードで確認

### 4. 管理画面テスト

#### メニュー管理
1. http://localhost:8000/admin/orders/menuitem/
2. メニュー項目を追加・編集
3. 売り切れ設定を変更

#### 注文管理
1. http://localhost:8000/admin/orders/order/
2. 注文一覧を確認
3. ステータスを変更（pending → cooking → ready → served）

#### 会計管理
1. http://localhost:8000/admin/orders/payment/
2. 会計依頼を確認
3. 支払い方法を選択して完了

---

## トラブルシューティング

### エラー: `ModuleNotFoundError`

**原因**: 依存パッケージが未インストール

**解決方法**:
```bash
pip install -r requirements.txt
```

---

### エラー: `Webhook設定失敗`

**原因**: ngrokが起動していない、またはURL不正

**解決方法**:
1. ngrokが起動していることを確認
2. `.env`の`TELEGRAM_WEBHOOK_URL`が正しいか確認
3. Webhook再設定:
   ```bash
   python manage.py delete_telegram_webhook
   python manage.py set_telegram_webhook
   ```

---

### エラー: `Telegram Botが応答しない`

**原因**: Webhookが正しく設定されていない

**解決方法**:
1. Webhook情報確認:
   ```
   https://api.telegram.org/bot{TOKEN}/getWebhookInfo
   ```
2. `pending_update_count`が増え続ける場合、Webhookエンドポイントにエラーあり
3. Django開発サーバーのログを確認

---

### エラー: `Mini Appsが表示されない`

**原因**: テンプレートパスまたはURL設定が不正

**解決方法**:
1. `settings.py`の`TEMPLATES`設定確認
2. `orders/templates/miniapp.html`が存在するか確認
3. URLパターン確認:
   ```python
   path('miniapp/', views.miniapp_view, name='miniapp'),
   ```

---

### ngrokのURL変更対応

ngrokを再起動すると、URLが変更されます。

**手順**:
1. 新しいngrok URLを取得
2. `.env`を更新:
   ```env
   TELEGRAM_WEBHOOK_URL=https://new-url.ngrok-free.app
   ```
3. Webhook再設定:
   ```bash
   python manage.py set_telegram_webhook
   ```
4. QRコード再生成:
   ```bash
   python manage.py generate_qrcodes
   ```

---

### データベースリセット

テストデータをリセットしたい場合:

```bash
# データベースファイル削除
rm db.sqlite3

# マイグレーション再実行
python manage.py migrate

# スーパーユーザー再作成
python manage.py createsuperuser

# テストデータ再作成
python manage.py create_test_data
```

---

## 本番環境への移行（参考）

開発環境でテストが完了したら、本番環境にデプロイできます。

### 主な変更点

1. **DATABASE**: SQLite → PostgreSQL/MySQL
2. **DEBUG**: `True` → `False`
3. **SECRET_KEY**: ランダムな文字列に変更
4. **ALLOWED_HOSTS**: ドメイン追加
5. **静的ファイル**: Nginx等で配信
6. **HTTPS**: Let's Encrypt等でSSL設定
7. **Gunicorn**: WSGIサーバー導入
8. **環境変数**: 本番環境専用の`.env`

詳細は別途デプロイガイドを参照してください。

---

## チェックリスト

セットアップ完了確認:

- [ ] Python 3.10以上インストール済み
- [ ] 依存パッケージインストール完了
- [ ] `.env`ファイル設定完了
- [ ] データベースマイグレーション完了
- [ ] スーパーユーザー作成完了
- [ ] テストデータ作成完了
- [ ] ngrokインストール・起動完了
- [ ] Telegram Webhook設定完了
- [ ] QRコード生成完了
- [ ] Django開発サーバー起動完了
- [ ] Telegram Botテスト成功
- [ ] Mini Appsテスト成功
- [ ] 管理画面アクセス成功

---

## サポート

問題が解決しない場合:

1. Djangoログを確認: コンソール出力
2. ngrokログを確認: ngrokコンソール出力
3. Telegram Webhook情報を確認: `getWebhookInfo` API
4. Issueを作成（GitHub）

---

## 次のステップ

テスト環境が完成したら:

1. 実際の店舗データを登録
2. メニュー写真をアップロード
3. QRコードを印刷してテーブルに設置
4. スタッフトレーニング
5. ソフトローンチ（限定テスト）
6. フィードバック収集・改善
7. 本番リリース

頑張ってください！ 🎉
