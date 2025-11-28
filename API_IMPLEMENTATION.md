# モバイルオーダーシステム API実装完了

## ✅ 実装完了内容

### 1. データモデル（Django Models）
- ✅ Store（店舗）
- ✅ Table（テーブル）
- ✅ Category（カテゴリ）
- ✅ MenuItem（メニュー項目）
- ✅ MenuItemImage（メニュー画像）
- ✅ Session（来店セッション）
- ✅ Order（注文）
- ✅ OrderItem（注文明細）
- ✅ StaffCall（店員呼び出し）
- ✅ Payment（会計）
- ✅ User（ユーザー/スタッフ）

### 2. REST API（Django REST Framework）
- ✅ メニューAPI（一覧、詳細、カテゴリフィルタ、売り切れ管理）
- ✅ セッションAPI（作成、復帰、完了）
- ✅ 注文API（作成、ステータス更新、ダッシュボード）
- ✅ 店員呼び出しAPI（作成、対応、解決）
- ✅ 会計API（依頼、完了、キャンセル）
- ✅ テーブルAPI（QRコード検索）
- ✅ カテゴリAPI
- ✅ ユーザーAPI

### 3. Django Admin（管理画面）
- ✅ 店舗管理
- ✅ テーブル管理（QRコードリンク付き）
- ✅ メニュー管理（売り切れ一括操作、画像インライン編集）
- ✅ セッション管理（合計金額表示）
- ✅ 注文管理（経過時間警告、ステータス一括更新、注文明細インライン）
- ✅ 店員呼び出し管理（対応時間表示）
- ✅ 会計管理
- ✅ ユーザー管理

### 4. テストデータ
- ✅ テストデータ作成コマンド（`python manage.py create_test_data`）
- ✅ サンプル店舗、テーブル、メニュー、セッション、注文データ

### 5. 自動テスト
- ✅ メニューAPI テスト（2テスト）
- ✅ セッションAPI テスト（2テスト）
- ✅ 注文API テスト（3テスト）
- ✅ 店員呼び出しAPI テスト（1テスト）
- ✅ 会計API テスト（3テスト）
- **合計: 11テスト - すべて成功 ✅**

## 🚀 使い方

### 開発サーバー起動
```bash
python manage.py runserver 0.0.0.0:8000
```

### テストデータ作成
```bash
python manage.py create_test_data
```

### テスト実行
```bash
python manage.py test orders --verbosity=2
```

### 管理画面アクセス
```
URL: http://localhost:8000/admin/
管理者: username=admin, password=admin123
料理人: username=chef1, password=chef123
スーパーバイザ: username=supervisor1, password=super123
```

## 📡 API エンドポイント

### メニュー関連
- `GET /api/menu-items/` - メニュー一覧取得
- `GET /api/menu-items/{id}/` - メニュー詳細取得
- `GET /api/menu-items/?category_id={id}` - カテゴリフィルタ
- `GET /api/menu-items/?available_only=true` - 提供可能のみ
- `POST /api/menu-items/{id}/toggle_available/` - 売り切れ切替（要認証）

### セッション関連
- `POST /api/sessions/` - セッション作成・復帰
- `GET /api/sessions/?session_code={code}` - セッション検索
- `GET /api/sessions/{id}/orders/` - セッションの全注文取得
- `POST /api/sessions/{id}/complete/` - セッション完了

### 注文関連
- `POST /api/orders/` - 注文作成
- `GET /api/orders/?session_id={id}` - セッションの注文一覧
- `POST /api/orders/{id}/update_status/` - ステータス更新（要認証）
- `GET /api/orders/dashboard/` - 調理ダッシュボード用データ（要認証）

### 店員呼び出し関連
- `POST /api/staff-calls/` - 店員呼び出し
- `GET /api/staff-calls/?pending_only=true` - 未対応の呼び出し
- `POST /api/staff-calls/{id}/respond/` - 対応開始（要認証）
- `POST /api/staff-calls/{id}/resolve/` - 解決（要認証）

### 会計関連
- `POST /api/payments/` - 会計依頼
- `GET /api/payments/?pending_only=true` - 会計待ち一覧
- `POST /api/payments/{id}/complete/` - 会計完了（要認証）
- `POST /api/payments/{id}/cancel/` - 会計キャンセル

### テーブル関連
- `GET /api/tables/by_qr_code/?qr_code_url={url}` - QRコードでテーブル検索

### カテゴリ関連
- `GET /api/categories/?store_id={id}` - 店舗のカテゴリ一覧

## 📊 API使用例

### 1. セッション作成
```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "qr_code_url": "https://t.me/yourbot?start=table-A-1",
    "party_size": 4
  }'
```

### 2. 注文作成
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_code": "TBL1-20241128-ABC123",
    "telegram_user_id": "user001",
    "telegram_username": "田中太郎",
    "items": [
      {
        "menu_item_id": 1,
        "quantity": 2,
        "note": "ドレッシング少なめ"
      },
      {
        "menu_item_id": 7,
        "quantity": 2
      }
    ]
  }'
```

### 3. 店員呼び出し
```bash
curl -X POST http://localhost:8000/api/staff-calls/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_code": "TBL1-20241128-ABC123",
    "reason": "water",
    "message": "お水を2つください"
  }'
```

### 4. 会計依頼
```bash
curl -X POST http://localhost:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_code": "TBL1-20241128-ABC123"
  }'
```

## 🧪 テストデータ

### テーブル
- A-1, A-2, A-3
- B-1, B-2, B-3
- C-1, C-2

### カテゴリ
- 前菜
- メイン
- 飲み物
- デザート

### メニュー（11品）
- シーザーサラダ (¥850)
- 枝豆 (¥400)
- 唐揚げ (¥800)
- トマトパスタ (¥1,200) - **売り切れ**
- ハンバーグステーキ (¥1,500)
- カルボナーラ (¥1,300)
- ビール (¥600)
- ハイボール (¥500)
- ウーロン茶 (¥300)
- チーズケーキ (¥600)
- アイスクリーム (¥400)

### サンプルセッション
- テーブル A-1: 4人、注文2件（1件提供済み、1件調理中）
- テーブル B-1: 2人、注文1件（未調理）

## 🔧 次のステップ

### Telegram Bot統合
1. `python-telegram-bot`のインストール
2. Bot トークンの設定
3. Mini Apps用のWebhookエンドポイント実装
4. QRコード生成機能の実装

### 追加機能
- [ ] メニュー画像アップロード機能
- [ ] レポート機能（日次売上、人気商品）
- [ ] リアルタイム通知（WebSocket）
- [ ] 多言語対応

### 本番環境デプロイ
- [ ] PostgreSQL設定
- [ ] Nginx + Gunicorn設定
- [ ] HTTPS設定
- [ ] 環境変数化（SECRET_KEY等）

## 📝 技術スタック

- **Backend**: Django 5.0 + Django REST Framework 3.15
- **Database**: SQLite (開発) / PostgreSQL (本番推奨)
- **認証**: Session Authentication + Basic Authentication
- **API**: RESTful API with DRF
- **Admin**: Django Admin (カスタマイズ済み)
- **Testing**: Django TestCase + DRF APIClient

## 📄 ライセンス

MIT License

---

**実装完了日**: 2024-11-28  
**バージョン**: 1.0  
**ステータス**: ✅ 完了（Telegram Bot統合は次フェーズ）
