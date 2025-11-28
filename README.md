# TelBot Order Django

Telegram Bot/Mini Appsを使用した飲食店向けモバイルオーダーシステム

## プロジェクト概要

顧客がQRコードをスキャンしてTelegram Mini Appsからメニューを閲覧・注文し、店舗側が注文状況を管理できるシステムです。

## ✨ 主な機能

### 顧客向け機能（Telegram Mini Apps）
- ✅ QRコードスキャンでセッション開始
- ✅ 商品画像付きメニュー閲覧
- ✅ グループ注文（複数人が同時注文可能）
- ✅ 追加注文機能
- ✅ 注文履歴確認
- ✅ 店員呼び出し（理由選択式）
- ✅ 会計依頼

### 店舗運用機能（管理画面）
- ✅ 注文ダッシュボード（リアルタイム表示）
- ✅ メニュー管理・編集
- ✅ 商品画像アップロード
- ✅ 売り切れ管理
- ✅ 調理ステータス管理
- ✅ 会計処理（テーブル単位一括会計）
- ✅ 売上管理

## 🚀 クイックスタート

### 必要要件
- Python 3.10以上
- pip
- ngrok（ローカル開発用）
- Telegramアカウント

### セットアップ（5分）

1. **リポジトリクローン**
   ```bash
   git clone https://github.com/YOUR_USERNAME/TelBotOrderDjango.git
   cd TelBotOrderDjango
   ```

2. **依存パッケージインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **環境変数設定**
   ```bash
   # .envファイル作成
   cp .env.example .env
   
   # .envを編集（Bot Token等を設定）
   ```

4. **データベースセットアップ**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py create_test_data
   ```

5. **ngrok起動（別ターミナル）**
   ```bash
   ngrok http 8000
   ```

6. **Webhook設定**
   ```bash
   # .envのTELEGRAM_WEBHOOK_URLをngrokのURLに更新
   python manage.py set_telegram_webhook
   python manage.py generate_qrcodes
   ```

7. **開発サーバー起動**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

8. **動作確認**
   - Telegram: `@mobail_order_bot` に `/start` を送信
   - 管理画面: http://localhost:8000/admin/
   - Mini Apps: http://localhost:8000/miniapp/?table_id=1

詳細は [TEST_ENVIRONMENT_SETUP.md](TEST_ENVIRONMENT_SETUP.md) を参照してください。

## 📚 ドキュメント

### 設計ドキュメント
- **[data_model.md](data_model.md)** - データモデル設計書（11エンティティ）
- **[functional_design.md](functional_design.md)** - 機能詳細設計書
- **[screen_design.md](screen_design.md)** - 画面詳細設計書（16画面）
- **[youken.md](youken.md)** - システム開発要件
- **[DESIGN_SUMMARY.md](DESIGN_SUMMARY.md)** - 設計サマリー

### 実装ドキュメント
- **[API_IMPLEMENTATION.md](API_IMPLEMENTATION.md)** - REST API実装レポート
- **[TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md)** - Telegram Bot環境セットアップガイド
- **[TELEGRAM_BOT_IMPLEMENTATION.md](TELEGRAM_BOT_IMPLEMENTATION.md)** - Telegram Bot実装ガイド
- **[TELEGRAM_BOT_TEST_CHECKLIST.md](TELEGRAM_BOT_TEST_CHECKLIST.md)** - テストチェックリスト
- **[TELEGRAM_BOT_QUICK_REFERENCE.md](TELEGRAM_BOT_QUICK_REFERENCE.md)** - クイックリファレンス
- **[TEST_ENVIRONMENT_SETUP.md](TEST_ENVIRONMENT_SETUP.md)** - テスト環境セットアップ手順書

## 🎨 モックアップ

全画面の動作するHTMLモックアップを作成しました：

- **[モックアップ一覧](mockups/index.html)** - 全画面へのインデックス
- **顧客向け画面**: 11画面（QRスキャン、メニュー、注文、会計など）
- **店舗運用画面**: 5画面（調理ダッシュボード、メニュー管理、売上レポートなど）

## 🛠 技術スタック

- **Backend**: Python 3.13, Django 5.0
- **API**: Django REST Framework 3.14
- **Database**: SQLite（開発）/ PostgreSQL（本番推奨）
- **Frontend（顧客）**: Telegram Bot & Mini Apps
- **Frontend（店舗）**: Django Admin + カスタムダッシュボード
- **画像処理**: Pillow 10.4
- **Telegram SDK**: python-telegram-bot 21.0
- **QRコード**: qrcode 7.4.2

## 📊 データモデル

11個のエンティティで構成：

1. **Store** - 店舗情報
2. **Table** - テーブル情報
3. **Category** - メニューカテゴリ
4. **MenuItem** - メニュー項目
5. **MenuItemImage** - メニュー画像
6. **Session** - 来店セッション
7. **Order** - 注文
8. **OrderItem** - 注文明細
9. **StaffCall** - 店員呼び出し
10. **Payment** - 会計
11. **User** - ユーザー/店舗スタッフ

詳細は [data_model.md](data_model.md) を参照。

## 🔌 API エンドポイント

60以上のREST APIエンドポイントを提供：

- メニュー管理: `/api/menu-items/`
- セッション管理: `/api/sessions/`
- 注文管理: `/api/orders/`
- 会計管理: `/api/payments/`
- 店員呼び出し: `/api/staff-calls/`

詳細は [API_IMPLEMENTATION.md](API_IMPLEMENTATION.md) を参照。

## 📱 Telegram Bot情報

- **BOT Name**: モバイルオーダーBOT
- **Bot Username**: @mobail_order_bot
- **Mini App Title**: OK-Mobile-Order-System

### 利用可能なコマンド
- `/start` - ボット起動、ウェルカムメッセージ
- `/help` - ヘルプ表示
- `/menu` - メニュー表示
- `/order` - 注文履歴確認
- `/status` - 注文状況確認

## 📂 ディレクトリ構造

```
TelBotOrderDjango/
├── mobile_order_system/    # Djangoプロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── orders/                 # メインアプリケーション
│   ├── models.py          # データモデル定義
│   ├── views.py           # ビュー（ViewSets）
│   ├── serializers.py     # DRF Serializers
│   ├── urls.py            # URLルーティング
│   ├── admin.py           # 管理画面設定
│   ├── telegram_bot.py    # Telegram Bot実装
│   ├── templates/         # HTMLテンプレート
│   │   └── miniapp.html  # Mini Apps UI
│   ├── management/        # 管理コマンド
│   │   └── commands/
│   │       ├── create_test_data.py
│   │       ├── set_telegram_webhook.py
│   │       ├── delete_telegram_webhook.py
│   │       └── generate_qrcodes.py
│   └── migrations/        # マイグレーションファイル
├── media/                 # アップロードファイル
│   ├── menu_items/       # メニュー画像
│   └── qrcodes/          # テーブルQRコード
├── mockups/               # HTMLモックアップ
│   ├── customer/         # 顧客向け画面
│   ├── staff/            # 店舗運用画面
│   └── index.html        # モック一覧
├── requirements.txt
├── .env.example
├── .gitignore
└── manage.py
```

## ✅ 開発状況

### Phase 1: 設計・基盤構築（完了）
- [x] システム要件定義
- [x] データモデル設計（11モデル）
- [x] 機能詳細設計
- [x] 画面詳細設計（16画面）
- [x] HTMLモックアップ作成
- [x] Djangoプロジェクトセットアップ
- [x] モデル定義・マイグレーション
- [x] Django Admin管理画面カスタマイズ

### Phase 2: REST API実装（完了）
- [x] REST API実装（60以上のエンドポイント）
- [x] Serializers実装
- [x] ViewSets実装
- [x] URLルーティング設定
- [x] 自動テスト作成（11テスト、全成功）
- [x] テストデータ作成コマンド

### Phase 3: Telegram Bot統合（完了）
- [x] Telegram Bot実装
  - [x] Webhook受信エンドポイント
  - [x] コマンドハンドラー（/start, /help, /menu等）
  - [x] インラインキーボード
  - [x] 通知機能
- [x] Telegram Mini Apps UI（HTML/CSS/JS）
- [x] QRコード生成機能
- [x] 環境セットアップドキュメント
- [x] テストチェックリスト

### Phase 4: 追加機能（計画中）
- [ ] リアルタイム通知（WebSocket）
- [ ] メニュー画像アップロード機能（完全版）
- [ ] 売上レポート機能（グラフ表示）
- [ ] 多言語対応（英語、中国語）
- [ ] パフォーマンス最適化

## 🧪 テスト

### 自動テスト実行

```bash
python manage.py test
```

**テスト結果**:
```
Ran 11 tests in 1.351s
OK ✅
```

テスト対象:
- Store, Table, Category, MenuItem CRUD
- Session作成・管理
- Order作成・ステータス更新
- Payment処理
- API認証・権限

## 🌐 本番環境デプロイ

### 推奨構成
- **Webサーバー**: Nginx
- **WSGIサーバー**: Gunicorn
- **データベース**: PostgreSQL
- **SSL**: Let's Encrypt
- **静的ファイル**: Nginx配信
- **メディアファイル**: S3 / CloudFlare R2

### 環境変数（本番環境）
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host/db
TELEGRAM_WEBHOOK_URL=https://yourdomain.com
```

詳細なデプロイ手順は別途作成予定。

## 🤝 貢献

プルリクエスト歓迎！

1. Fork
2. Feature branchを作成 (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Pull Request作成

## 📝 ライセンス

Private Project（商用利用の場合はライセンス確認が必要）

## 🙏 謝辞

- Django & Django REST Framework コミュニティ
- python-telegram-bot プロジェクト
- Telegram Bot API

## 📞 サポート

- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/TelBotOrderDjango/issues)
- Email: your-email@example.com

---

**開発者**: AI駆動開発  
**最終更新**: 2024-11-28
