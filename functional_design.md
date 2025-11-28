# 機能詳細設計書

## 1. システム全体アーキテクチャ

### 1.1 システム構成
```
┌─────────────────┐
│  Telegram App   │
│  (Mini Apps)    │
│  顧客インターフェース │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Django Server  │
│  ┌───────────┐  │
│  │ REST API  │  │
│  ├───────────┤  │
│  │ Bot API   │  │
│  ├───────────┤  │
│  │ Business  │  │
│  │  Logic    │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │
└─────────────────┘

┌─────────────────┐
│  Web Browser    │
│  店舗管理画面    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│ Django Admin +  │
│ Custom Dashboard│
└─────────────────┘
```

### 1.2 技術スタック詳細
- **Backend Framework**: Django 5.0
- **API Framework**: Django REST Framework 3.14
- **Database**: SQLite (開発), PostgreSQL (本番推奨)
- **Telegram SDK**: python-telegram-bot 21.0
- **Image Processing**: Pillow 10.4
- **Frontend (顧客)**: Telegram Mini Apps (HTML/CSS/JS)
- **Frontend (店舗)**: Django Admin + カスタムダッシュボード

---

## 2. 顧客向け機能詳細

### 2.1 QRコードスキャン・セッション開始

#### 機能概要
テーブルに設置されたQRコードをスキャンし、来店セッションを開始する。

#### 処理フロー
1. 顧客がスマホカメラでQRコードをスキャン
2. QRコードのURLパラメータから`table_id`を取得
3. Telegram Mini Appsが起動
4. バックエンドに`table_id`を送信
5. バックエンドが既存アクティブセッションを確認
   - 既存セッションあり → セッション復帰確認画面表示
   - 既存セッションなし → 来店人数入力画面表示
6. 来店人数確定でセッション作成
7. セッションコードをローカルストレージに保存
8. メニュー一覧画面に遷移

#### API仕様

**エンドポイント**: `POST /api/sessions/start/`

**リクエスト**:
```json
{
  "table_id": 1,
  "telegram_chat_id": "123456789",
  "telegram_user_id": "987654321",
  "telegram_username": "user_name"
}
```

**レスポンス（新規セッション作成時）**:
```json
{
  "status": "new_session",
  "session": {
    "session_code": "TBL1-20241128-001",
    "table_number": "A-1",
    "party_size_required": true
  }
}
```

**レスポンス（既存セッション存在時）**:
```json
{
  "status": "existing_session",
  "session": {
    "session_code": "TBL1-20241128-001",
    "table_number": "A-1",
    "party_size": 4,
    "started_at": "2024-11-28T12:30:00+09:00"
  }
}
```

**エンドポイント**: `POST /api/sessions/create/`

**リクエスト**:
```json
{
  "table_id": 1,
  "party_size": 4,
  "telegram_chat_id": "123456789"
}
```

**レスポンス**:
```json
{
  "session_code": "TBL1-20241128-001",
  "table": {
    "id": 1,
    "table_number": "A-1"
  },
  "party_size": 4,
  "status": "active",
  "started_at": "2024-11-28T12:30:00+09:00"
}
```

#### ビジネスロジック
- セッションコード生成ルール: `TBL{table_id}-{YYYYMMDD}-{連番3桁}`
- 同一テーブルで`status='active'`のセッションは1つのみ
- `started_at`は現在時刻（Asia/Tokyo）
- 来店人数は1〜99人まで入力可能

---

### 2.2 メニュー閲覧

#### 機能概要
カテゴリ別にメニュー一覧を表示し、商品詳細を確認できる。

#### 処理フロー
1. メニュー一覧画面表示
2. カテゴリタブで絞り込み
3. 商品カードをタップで詳細モーダル表示
4. スクロールで次のページを読み込み（無限スクロール）

#### API仕様

**エンドポイント**: `GET /api/menu/categories/`

**クエリパラメータ**:
- `store_id`: 店舗ID（必須）

**レスポンス**:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "前菜",
      "display_order": 1,
      "item_count": 12
    },
    {
      "id": 2,
      "name": "メイン",
      "display_order": 2,
      "item_count": 25
    }
  ]
}
```

**エンドポイント**: `GET /api/menu/items/`

**クエリパラメータ**:
- `store_id`: 店舗ID（必須）
- `category_id`: カテゴリID（オプション）
- `page`: ページ番号（デフォルト: 1）
- `page_size`: 1ページあたりの件数（デフォルト: 20）

**レスポンス**:
```json
{
  "count": 50,
  "next": "/api/menu/items/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "シーザーサラダ",
      "description": "新鮮なロメインレタスとパルメザンチーズ",
      "price": "850.00",
      "category": {
        "id": 1,
        "name": "前菜"
      },
      "thumbnail_url": "/media/menu_items/1/1/thumbnail.jpg",
      "is_available": true,
      "max_quantity_per_order": 10
    }
  ]
}
```

**エンドポイント**: `GET /api/menu/items/{id}/`

**レスポンス**:
```json
{
  "id": 1,
  "name": "シーザーサラダ",
  "description": "新鮮なロメインレタスとクリーミーなシーザードレッシング、パルメザンチーズをトッピング",
  "price": "850.00",
  "category": {
    "id": 1,
    "name": "前菜"
  },
  "image_url": "/media/menu_items/1/1/large.jpg",
  "thumbnail_url": "/media/menu_items/1/1/thumbnail.jpg",
  "is_available": true,
  "max_quantity_per_order": 10,
  "allergens": null
}
```

#### UI要件
- サムネイル画像: 400x300px（lazy loading）
- 詳細画像: 800x600px
- 売り切れ商品: グレーアウト表示、注文不可
- 価格は税込表示

---

### 2.3 注文機能

#### 機能概要
メニューから商品を選択し、数量を決めて注文する。

#### 処理フロー
1. 商品詳細モーダルで数量を選択（1〜最大数量）
2. カートに追加ボタンをタップ
3. カート画面で注文内容を確認
4. 備考欄入力（アレルギー対応など）
5. 注文確定ボタンをタップ
6. 注文完了画面表示
7. メニュー一覧に戻る（追加注文可能）

#### API仕様

**エンドポイント**: `POST /api/orders/create/`

**リクエスト**:
```json
{
  "session_code": "TBL1-20241128-001",
  "telegram_user_id": "987654321",
  "telegram_username": "user_name",
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2,
      "note": "ドレッシング少なめ"
    },
    {
      "menu_item_id": 5,
      "quantity": 1,
      "note": null
    }
  ]
}
```

**レスポンス**:
```json
{
  "order_id": 123,
  "order_number": 1,
  "session_code": "TBL1-20241128-001",
  "total_amount": "2550.00",
  "status": "pending",
  "ordered_at": "2024-11-28T12:35:00+09:00",
  "items": [
    {
      "menu_item_name": "シーザーサラダ",
      "quantity": 2,
      "unit_price": "850.00",
      "subtotal": "1700.00"
    },
    {
      "menu_item_name": "トマトパスタ",
      "quantity": 1,
      "unit_price": "850.00",
      "subtotal": "850.00"
    }
  ]
}
```

#### バリデーション
- セッションが`active`または`payment_requested`状態であること
- `payment_requested`の場合は確認ダイアログ表示
- 商品が`is_available=true`, `is_active=true`であること
- 数量が1以上、`max_quantity_per_order`以下であること
- カートは最低1品以上

#### ビジネスロジック
- 注文番号はセッション内の連番（1, 2, 3...）
- 合計金額は自動計算（`sum(quantity * unit_price)`）
- 注文時の商品名・単価をスナップショット保存
- `ordered_at`は現在時刻（Asia/Tokyo）
- 注文完了時にTelegram通知（店舗側）

---

### 2.4 注文履歴確認

#### 機能概要
現在のセッションで注文した履歴を確認する。

#### API仕様

**エンドポイント**: `GET /api/orders/history/`

**クエリパラメータ**:
- `session_code`: セッションコード（必須）

**レスポンス**:
```json
{
  "session": {
    "session_code": "TBL1-20241128-001",
    "table_number": "A-1",
    "party_size": 4,
    "started_at": "2024-11-28T12:30:00+09:00"
  },
  "orders": [
    {
      "order_number": 1,
      "total_amount": "2550.00",
      "status": "served",
      "ordered_at": "2024-11-28T12:35:00+09:00",
      "items": [
        {
          "menu_item_name": "シーザーサラダ",
          "quantity": 2,
          "unit_price": "850.00",
          "status": "served"
        }
      ]
    },
    {
      "order_number": 2,
      "total_amount": "1200.00",
      "status": "cooking",
      "ordered_at": "2024-11-28T12:45:00+09:00",
      "items": [
        {
          "menu_item_name": "ビール",
          "quantity": 2,
          "unit_price": "600.00",
          "status": "cooking"
        }
      ]
    }
  ],
  "total_amount": "3750.00"
}
```

#### UI要件
- 注文ステータスバッジ表示
  - `pending`: 注文受付済み（オレンジ）
  - `cooking`: 調理中（青）
  - `ready`: 調理完了（緑）
  - `served`: 提供済み（グレー）
- 注文時刻を相対時間で表示（例: 10分前）
- キャンセルされた注文は非表示

---

### 2.5 店員呼び出し

#### 機能概要
店員を呼び出す際に理由を選択して通知する。

#### 処理フロー
1. 店員呼び出しボタンをタップ
2. 理由選択モーダル表示
3. 理由を選択（必須）
4. 追加メッセージ入力（オプション）
5. 呼び出し確定
6. 完了画面表示（店員到着まで待機）

#### API仕様

**エンドポイント**: `POST /api/staff-calls/create/`

**リクエスト**:
```json
{
  "session_code": "TBL1-20241128-001",
  "reason": "water",
  "message": "冷たいお水をお願いします"
}
```

**レスポンス**:
```json
{
  "id": 45,
  "session_code": "TBL1-20241128-001",
  "reason": "water",
  "reason_display": "お水が欲しい",
  "message": "冷たいお水をお願いします",
  "status": "pending",
  "called_at": "2024-11-28T12:50:00+09:00"
}
```

#### 理由選択肢
- `water`: お水が欲しい
- `payment`: 会計したい
- `question`: 質問がある
- `complaint`: 苦情・問題
- `other`: その他

#### ビジネスロジック
- 呼び出し時にTelegram通知（店舗側）
- セッションステータスを`calling_staff`に更新
- 店員が対応開始で`status='in_progress'`、対応完了で`status='resolved'`
- 解決済みでセッションステータスを元の状態に戻す

---

### 2.6 会計機能

#### 機能概要
テーブル単位で会計依頼を行う。

#### 処理フロー
1. 会計ボタンをタップ
2. 注文合計金額を表示
3. 会計依頼確認
4. 会計依頼確定
5. レシート画面表示（QRコード含む）
6. レジに持参して支払い
7. 店員がPOSレジで決済完了

#### API仕様

**エンドポイント**: `POST /api/payments/request/`

**リクエスト**:
```json
{
  "session_code": "TBL1-20241128-001"
}
```

**レスポンス**:
```json
{
  "payment_id": 78,
  "session_code": "TBL1-20241128-001",
  "total_amount": "5230.00",
  "status": "pending",
  "requested_at": "2024-11-28T13:15:00+09:00",
  "orders": [
    {
      "order_number": 1,
      "total_amount": "2550.00"
    },
    {
      "order_number": 2,
      "total_amount": "2680.00"
    }
  ]
}
```

**エンドポイント**: `POST /api/payments/cancel/`

**リクエスト**:
```json
{
  "session_code": "TBL1-20241128-001"
}
```

**レスポンス**:
```json
{
  "status": "cancelled",
  "session_status": "active",
  "message": "会計依頼をキャンセルしました。追加注文が可能です。"
}
```

#### ビジネスロジック
- セッションステータスを`payment_requested`に更新
- `status='cancelled'`以外の全注文を集計
- 会計依頼後も追加注文可能（会計キャンセル必要）
- POSレジで決済完了後、`status='paid'`、セッション`status='completed'`

---

### 2.7 セッション復帰

#### 機能概要
Telegram Mini Appsを再度開いた際に、前回のセッションに復帰できる。

#### 処理フロー
1. Mini Apps起動
2. ローカルストレージから`session_code`を取得
3. セッション有効性確認API呼び出し
4. 有効な場合、復帰確認ダイアログ表示
5. 「はい」→ セッション復帰、メニュー一覧表示
6. 「いいえ」→ QRスキャン画面表示

#### API仕様

**エンドポイント**: `GET /api/sessions/validate/`

**クエリパラメータ**:
- `session_code`: セッションコード

**レスポンス（有効な場合）**:
```json
{
  "valid": true,
  "session": {
    "session_code": "TBL1-20241128-001",
    "table_number": "A-1",
    "status": "active",
    "started_at": "2024-11-28T12:30:00+09:00"
  }
}
```

**レスポンス（無効な場合）**:
```json
{
  "valid": false,
  "reason": "session_completed"
}
```

#### バリデーション
- セッションが`active`、`calling_staff`、`payment_requested`のいずれか
- `started_at`から24時間以内

---

## 3. 店舗運用機能詳細

### 3.1 調理ダッシュボード

#### 機能概要
注文をリアルタイムで表示し、調理ステータスを管理する。

#### 画面レイアウト
```
┌───────────────────────────────────────────┐
│ 調理ダッシュボード        [自動更新: ON]  │
├───────────────────────────────────────────┤
│ [未調理(5)] [調理中(3)] [完了(2)] [全て] │
├───────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ テーブル: A-1  注文#1  10分前       │ │
│ │ シーザーサラダ x2  [調理開始]       │ │
│ │ トマトパスタ x1    [調理開始]       │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ テーブル: B-3  注文#2  5分前  調理中│ │
│ │ ビール x2          [完了]           │ │
│ │ 枝豆 x1            [完了]           │ │
│ └─────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

#### API仕様

**エンドポイント**: `GET /api/dashboard/orders/`

**クエリパラメータ**:
- `store_id`: 店舗ID（必須）
- `status`: ステータスフィルター（オプション）
- `limit`: 取得件数（デフォルト: 50）

**レスポンス**:
```json
{
  "pending_count": 5,
  "cooking_count": 3,
  "ready_count": 2,
  "orders": [
    {
      "id": 123,
      "session": {
        "session_code": "TBL1-20241128-001",
        "table_number": "A-1"
      },
      "order_number": 1,
      "status": "pending",
      "ordered_at": "2024-11-28T12:35:00+09:00",
      "elapsed_minutes": 10,
      "items": [
        {
          "id": 456,
          "menu_item_name": "シーザーサラダ",
          "quantity": 2,
          "status": "pending",
          "note": "ドレッシング少なめ"
        }
      ]
    }
  ]
}
```

**エンドポイント**: `PATCH /api/orders/{id}/status/`

**リクエスト**:
```json
{
  "status": "cooking"
}
```

**レスポンス**:
```json
{
  "id": 123,
  "status": "cooking",
  "cooking_started_at": "2024-11-28T12:45:00+09:00"
}
```

**エンドポイント**: `PATCH /api/order-items/{id}/status/`

**リクエスト**:
```json
{
  "status": "ready"
}
```

#### UI要件
- WebSocketまたはポーリング（10秒間隔）で自動更新
- 経過時間に応じて背景色変更
  - 10分未満: 白
  - 10-20分: 黄色
  - 20分以上: 赤
- ステータス変更はドラッグ&ドロップまたはボタンクリック
- 音声通知（新規注文時）

---

### 3.2 メニュー管理

#### 機能概要
メニューの登録・編集・削除、画像アップロードを行う。

#### 画面遷移
```
メニュー一覧
  ├→ メニュー新規登録
  └→ メニュー編集
      ├→ 画像アップロード
      └→ 削除確認
```

#### Django Admin拡張
- カテゴリごとにグループ表示
- インライン編集（価格、在庫状況）
- 一括売り切れ設定
- 画像プレビュー表示

#### 画像アップロード仕様
- 対応形式: JPEG, PNG, WebP
- 最大ファイルサイズ: 2MB
- 自動リサイズ:
  - サムネイル: 400x300px
  - 大サイズ: 800x600px
- EXIF情報削除（プライバシー保護）
- 保存パス: `/media/menu_items/{store_id}/{menu_item_id}/`

---

### 3.3 売り切れ管理

#### 機能概要
商品の提供可能状態を手動で変更する。

#### API仕様

**エンドポイント**: `PATCH /api/menu/items/{id}/availability/`

**リクエスト**:
```json
{
  "is_available": false
}
```

**レスポンス**:
```json
{
  "id": 1,
  "name": "シーザーサラダ",
  "is_available": false,
  "updated_at": "2024-11-28T14:00:00+09:00"
}
```

#### UI要件
- ダッシュボードから即座に切り替え可能
- トグルスイッチまたはチェックボックス
- 変更履歴を記録（将来機能）

---

### 3.4 会計処理

#### 機能概要
会計依頼を受けてレジで決済処理を行う。

#### 処理フロー
1. 会計依頼一覧画面で対象セッションを選択
2. レシート印刷
3. 顧客から支払いを受ける
4. 支払い方法を選択
5. 決済完了ボタンをクリック
6. セッション完了

#### API仕様

**エンドポイント**: `GET /api/payments/pending/`

**クエリパラメータ**:
- `store_id`: 店舗ID

**レスポンス**:
```json
{
  "payments": [
    {
      "id": 78,
      "session": {
        "session_code": "TBL1-20241128-001",
        "table_number": "A-1"
      },
      "total_amount": "5230.00",
      "requested_at": "2024-11-28T13:15:00+09:00",
      "elapsed_minutes": 5
    }
  ]
}
```

**エンドポイント**: `POST /api/payments/{id}/complete/`

**リクエスト**:
```json
{
  "payment_method": "cash"
}
```

**レスポンス**:
```json
{
  "id": 78,
  "status": "paid",
  "payment_method": "cash",
  "paid_at": "2024-11-28T13:20:00+09:00",
  "session_status": "completed"
}
```

---

### 3.5 売上管理

#### 機能概要
日次・月次の売上レポートを表示する。

#### API仕様

**エンドポイント**: `GET /api/reports/sales/`

**クエリパラメータ**:
- `store_id`: 店舗ID
- `start_date`: 開始日（YYYY-MM-DD）
- `end_date`: 終了日（YYYY-MM-DD）

**レスポンス**:
```json
{
  "period": {
    "start_date": "2024-11-01",
    "end_date": "2024-11-28"
  },
  "summary": {
    "total_sales": "1250000.00",
    "order_count": 324,
    "avg_order_amount": "3858.02",
    "total_customers": 856
  },
  "daily_sales": [
    {
      "date": "2024-11-28",
      "sales": "45230.00",
      "orders": 12,
      "customers": 28
    }
  ],
  "top_items": [
    {
      "menu_item_name": "ビール",
      "quantity": 156,
      "sales": "93600.00"
    }
  ]
}
```

---

## 4. セキュリティ要件

### 4.1 認証・認可
- Telegram Mini Apps: Telegram認証（init data検証）
- 管理画面: Django認証（ユーザー名/パスワード）
- API: Token認証（将来的にJWT）

### 4.2 データ保護
- パスワードハッシュ化（Django標準）
- HTTPS通信必須（本番環境）
- CSRF保護有効化
- SQL Injection対策（ORM使用）

### 4.3 入力検証
- すべてのユーザー入力をバリデーション
- 数量・価格は正の数のみ許可
- XSS対策（エスケープ処理）

---

## 5. パフォーマンス要件

### 5.1 レスポンスタイム
- API応答時間: 300ms以内（95パーセンタイル）
- 画像読み込み: 1秒以内
- ダッシュボード更新: 1秒以内

### 5.2 同時アクセス
- 想定同時接続数: 100セッション
- ピーク時対応: 200セッション

### 5.3 最適化
- 画像lazy loading
- APIレスポンスキャッシング（5分）
- データベースインデックス最適化
- N+1クエリ防止（select_related, prefetch_related）

---

## 6. エラーハンドリング

### 6.1 エラーレスポンス形式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力内容に誤りがあります",
    "details": {
      "quantity": ["数量は1以上10以下で指定してください"]
    }
  }
}
```

### 6.2 エラーコード一覧
- `VALIDATION_ERROR`: バリデーションエラー
- `NOT_FOUND`: リソースが見つからない
- `SESSION_EXPIRED`: セッション期限切れ
- `ITEM_UNAVAILABLE`: 商品提供不可
- `PAYMENT_REQUIRED`: 会計依頼中
- `SERVER_ERROR`: サーバーエラー

---

## 7. 通知機能

### 7.1 Telegram通知
- 新規注文時: 店舗Telegram Botに通知
- 店員呼び出し時: 店舗Telegram Botに通知
- 会計依頼時: 店舗Telegram Botに通知

### 7.2 通知フォーマット
```
🔔 新規注文
テーブル: A-1
注文番号: #1
---
シーザーサラダ x2
トマトパスタ x1
---
合計: ¥2,550
注文時刻: 12:35
```

---

## 8. 今後の拡張機能

### 8.1 Phase 2
- 個別会計機能
- クーポン・割引機能
- 多言語対応（英語、中国語）

### 8.2 Phase 3
- 在庫管理自動化
- 予約システム連携
- 顧客分析ダッシュボード
- マルチ店舗対応

---

## 9. 開発優先順位

### Priority 1（MVP）
1. セッション開始・管理
2. メニュー閲覧
3. 注文機能
4. 調理ダッシュボード
5. 会計処理

### Priority 2
1. 注文履歴確認
2. 店員呼び出し
3. セッション復帰
4. 画像アップロード

### Priority 3
1. 売上管理
2. Telegram通知
3. リアルタイム更新（WebSocket）
