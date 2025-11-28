# データモデル設計書

## 要件整理結果

### 確認した仕様
1. **グループ注文**：同一テーブルで複数人が各自のスマホから同時に注文を追加可能
2. **追加注文**：初回注文後も追加オーダー可能
3. **会計単位**：テーブル単位での一括会計のみ
4. **在庫管理**：在庫管理機能は不要、売り切れは手動でメニューの提供可能フラグをOFFにする
5. **店員呼び出し**：呼び出し時に理由を選択可能

---

## エンティティ一覧

1. **Store**（店舗）
2. **Table**（テーブル）
3. **Category**（カテゴリ）
4. **MenuItem**（メニュー項目）
5. **MenuItemImage**（メニュー画像）
6. **Session**（来店セッション）
7. **Order**（注文）
8. **OrderItem**（注文明細）
9. **StaffCall**（店員呼び出し）
10. **Payment**（会計）
11. **User**（ユーザー/店舗スタッフ）

---

## エンティティ詳細設計

### 1. Store（店舗）
店舗の基本情報を管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 店舗ID |
| name | VARCHAR(100) | NOT NULL | 店舗名 |
| address | VARCHAR(255) | NULL | 住所 |
| phone | VARCHAR(20) | NULL | 電話番号 |
| business_hours | TEXT | NULL | 営業時間（JSON形式） |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 営業中フラグ |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

---

### 2. Table（テーブル）
店舗内のテーブル情報を管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | テーブルID |
| store_id | INTEGER | FK → Store(id), NOT NULL | 店舗ID |
| table_number | VARCHAR(20) | NOT NULL | テーブル番号 |
| qr_code_url | VARCHAR(255) | NOT NULL, UNIQUE | QRコードURL |
| capacity | INTEGER | NULL | 定員数 |
| is_available | BOOLEAN | NOT NULL, DEFAULT TRUE | 利用可能フラグ |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**INDEX**
- UNIQUE(store_id, table_number)

---

### 3. Category（カテゴリ）
メニューのカテゴリを管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | カテゴリID |
| store_id | INTEGER | FK → Store(id), NOT NULL | 店舗ID |
| name | VARCHAR(50) | NOT NULL | カテゴリ名 |
| display_order | INTEGER | NOT NULL, DEFAULT 0 | 表示順序 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 有効フラグ |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**INDEX**
- INDEX(store_id, display_order)

---

### 4. MenuItem（メニュー項目）
提供するメニュー商品を管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | メニューID |
| store_id | INTEGER | FK → Store(id), NOT NULL | 店舗ID |
| category_id | INTEGER | FK → Category(id), NULL | カテゴリID |
| name | VARCHAR(100) | NOT NULL | 商品名 |
| description | TEXT | NULL | 説明 |
| price | DECIMAL(10,2) | NOT NULL | 価格 |
| image_path | VARCHAR(500) | NULL | 商品画像ファイルパス |
| image_thumbnail_path | VARCHAR(500) | NULL | サムネイル画像パス |
| max_quantity_per_order | INTEGER | NULL, DEFAULT 10 | 1注文あたりの最大数量 |
| display_order | INTEGER | NOT NULL, DEFAULT 0 | 表示順序 |
| is_available | BOOLEAN | NOT NULL, DEFAULT TRUE | 提供可能フラグ（売り切れ管理） |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 有効フラグ（メニュー削除） |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**画像ファイル管理**
- 画像ファイルは`/media/menu_items/{store_id}/{menu_item_id}/`に保存
- オリジナル画像：`original.jpg` (最大2MB、推奨サイズ：1200x900px)
- サムネイル画像：`thumbnail.jpg` (自動生成、400x300px)
- 対応フォーマット：JPEG, PNG, WebP
- 画像未登録時：デフォルト画像（/static/images/no-image.png）を表示

**INDEX**
- INDEX(store_id, category_id, display_order)
- INDEX(is_available, is_active)

---

### 5. MenuItemImage（メニュー画像）
メニュー商品の画像ファイルを管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 画像ID |
| menu_item_id | INTEGER | FK → MenuItem(id), NOT NULL | メニューID |
| image_type | VARCHAR(20) | NOT NULL | 画像タイプ |
| file_path | VARCHAR(500) | NOT NULL | ファイルパス |
| file_size | INTEGER | NOT NULL | ファイルサイズ（バイト） |
| width | INTEGER | NULL | 画像幅（ピクセル） |
| height | INTEGER | NULL | 画像高さ（ピクセル） |
| mime_type | VARCHAR(50) | NOT NULL | MIMEタイプ |
| uploaded_at | DATETIME | NOT NULL | アップロード日時 |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**image_type値**
- `original`: オリジナル画像
- `thumbnail`: サムネイル画像（一覧表示用）
- `large`: 大サイズ画像（詳細表示用）

**INDEX**
- INDEX(menu_item_id, image_type)
- UNIQUE(menu_item_id, image_type)

---

### 6. Session（来店セッション）
顧客の来店から退店までの1セッションを管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | セッションID |
| store_id | INTEGER | FK → Store(id), NOT NULL | 店舗ID |
| table_id | INTEGER | FK → Table(id), NOT NULL | テーブルID |
| session_code | VARCHAR(50) | NOT NULL, UNIQUE | セッションコード（ユニーク識別子） |
| party_size | INTEGER | NOT NULL | 来店人数 |
| telegram_chat_id | VARCHAR(50) | NULL | Telegram Chat ID |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | ステータス |
| started_at | DATETIME | NOT NULL | 来店日時 |
| ended_at | DATETIME | NULL | 退店日時 |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**status値**
- `active`: 来店中
- `calling_staff`: 店員呼び出し中
- `payment_requested`: 会計依頼中（この状態でも会計キャンセル後に追加注文可能）
- `completed`: 完了
- `cancelled`: キャンセル

**INDEX**
- INDEX(table_id, status)
- INDEX(started_at)

---

### 7. Order（注文）
顧客からの注文単位を管理（1回の注文操作）

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 注文ID |
| session_id | INTEGER | FK → Session(id), NOT NULL | セッションID |
| telegram_user_id | VARCHAR(50) | NULL | 注文者のTelegram User ID |
| telegram_username | VARCHAR(100) | NULL | 注文者のTelegram Username |
| order_number | INTEGER | NOT NULL | 注文番号（session内での連番） |
| total_amount | DECIMAL(10,2) | NOT NULL | 合計金額 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | ステータス |
| ordered_at | DATETIME | NOT NULL | 注文日時 |
| cooking_started_at | DATETIME | NULL | 調理開始日時 |
| ready_at | DATETIME | NULL | 調理完了日時 |
| served_at | DATETIME | NULL | 提供日時 |
| cancelled_at | DATETIME | NULL | キャンセル日時 |
| cancelled_by | INTEGER | FK → User(id), NULL | キャンセル実行者（スタッフ） |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**status値**
- `pending`: 注文受付済み（未調理）
- `cooking`: 調理中
- `ready`: 調理完了（提供待ち、スーパーバイザ判断で提供）
- `served`: 提供済み
- `cancelled`: キャンセル（店舗側のみ可能）

**INDEX**
- INDEX(session_id, order_number)
- INDEX(status, ordered_at)

---

### 8. OrderItem（注文明細）
注文内の個別商品を管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 注文明細ID |
| order_id | INTEGER | FK → Order(id), NOT NULL | 注文ID |
| menu_item_id | INTEGER | FK → MenuItem(id), NOT NULL | メニューID |
| menu_item_name | VARCHAR(100) | NOT NULL | 商品名（スナップショット） |
| unit_price | DECIMAL(10,2) | NOT NULL | 単価（スナップショット） |
| quantity | INTEGER | NOT NULL | 数量 |
| subtotal | DECIMAL(10,2) | NOT NULL | 小計 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | ステータス |
| note | TEXT | NULL | 備考（アレルギー対応など） |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**status値**
- `pending`: 未調理
- `cooking`: 調理中
- `ready`: 調理完了
- `served`: 提供済み
- `cancelled`: キャンセル

**INDEX**
- INDEX(order_id)
- INDEX(status)

---

### 9. StaffCall（店員呼び出し）
顧客からの店員呼び出しを管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 呼び出しID |
| session_id | INTEGER | FK → Session(id), NOT NULL | セッションID |
| reason | VARCHAR(20) | NOT NULL | 理由 |
| message | TEXT | NULL | メッセージ |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | ステータス |
| called_at | DATETIME | NOT NULL | 呼び出し日時 |
| responded_at | DATETIME | NULL | 対応開始日時 |
| resolved_at | DATETIME | NULL | 解決日時 |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**reason値**
- `water`: お水が欲しい
- `payment`: 会計したい
- `question`: 質問がある
- `complaint`: 苦情・問題
- `other`: その他

**status値**
- `pending`: 未対応
- `in_progress`: 対応中
- `resolved`: 解決済み

**INDEX**
- INDEX(session_id, status)
- INDEX(called_at)

---

### 10. Payment（会計）
テーブル単位の会計情報を管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 会計ID |
| session_id | INTEGER | FK → Session(id), NOT NULL, UNIQUE | セッションID |
| total_amount | DECIMAL(10,2) | NOT NULL | 合計金額 |
| payment_method | VARCHAR(20) | NULL | 支払い方法 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | ステータス |
| requested_at | DATETIME | NOT NULL | 会計依頼日時 |
| paid_at | DATETIME | NULL | 支払完了日時 |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**payment_method値**
- `cash`: 現金
- `credit_card`: クレジットカード
- `electronic`: 電子マネー
- NULL: 未設定（POSレジで決定）

**status値**
- `pending`: 会計待ち
- `paid`: 支払済み
- `cancelled`: キャンセル

**INDEX**
- INDEX(status, requested_at)

---

### 11. User（ユーザー/店舗スタッフ）
店舗運用システムのユーザー管理

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | ユーザーID |
| store_id | INTEGER | FK → Store(id), NOT NULL | 店舗ID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | ユーザー名 |
| email | VARCHAR(100) | NOT NULL, UNIQUE | メールアドレス |
| password_hash | VARCHAR(255) | NOT NULL | パスワードハッシュ |
| role | VARCHAR(20) | NOT NULL | 役割 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 有効フラグ |
| last_login_at | DATETIME | NULL | 最終ログイン日時 |
| created_at | DATETIME | NOT NULL | 作成日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

**role値**
- `admin`: 管理者
- `chef`: 料理人
- `supervisor`: スーパーバイザ
- `staff`: スタッフ

**INDEX**
- INDEX(store_id, role)

---

## ER図（リレーション）

```
Store 1 ──< * Table
Store 1 ──< * Category
Store 1 ──< * MenuItem
Store 1 ──< * User

Category 1 ──< * MenuItem

MenuItem 1 ──< * MenuItemImage
MenuItem 1 ──< * OrderItem

Table 1 ──< * Session

Session 1 ──< * Order
Session 1 ──< * StaffCall
Session 1 ──── 1 Payment (1対1)

Order 1 ──< * OrderItem
```

---

## 主要な業務フロー

### 1. 来店〜注文フロー
1. 顧客がQRコードをスキャン
   - 既存アクティブセッションがない場合 → `Session`作成（status: active）、来店人数を入力
   - 既存アクティブセッションがある場合 → 既存セッションに自動参加（来店人数入力スキップ）
2. メニューを閲覧 → `MenuItem`を取得（is_available=TRUE, is_active=TRUE）
3. 商品を選択して注文 → 数量制限チェック（max_quantity_per_order）→ `Order`と`OrderItem`を作成
4. 追加注文 → 同じSessionで新しい`Order`を作成

### 2. 調理〜提供フロー
1. 調理場ダッシュボードで注文一覧表示 → `OrderItem`単位で表示（status: pending）
2. 調理開始 → `OrderItem.status`を'cooking'に更新
3. 調理完了 → `OrderItem.status`を'ready'に更新（待ち時間の警告なし）
4. スーパーバイザがチェック後提供 → `OrderItem.status`を'served'に更新
5. 注文キャンセル（店舗側のみ） → `Order.status`を'cancelled'に更新、`cancelled_by`を記録

### 3. 会計フロー
1. 顧客が会計ボタンをクリック → `Payment`作成（status: pending）、Session.status='payment_requested'
2. 会計依頼後に追加注文したい場合 → 会計キャンセル → `Payment.status`を'cancelled'に更新、Session.status='active'に戻す → 追加注文可能
3. レシート印刷 → Sessionに紐づく全`Order`（cancelled以外）の合計を計算
4. POSレジで支払い → `Payment.status`を'paid'に更新、`payment_method`と`paid_at`を記録
5. セッション終了 → `Session.status`を'completed'に更新、`ended_at`を記録

### 4. 店員呼び出しフロー
1. 顧客が理由を選択して呼び出し → `StaffCall`作成（status: pending）
2. スタッフが対応開始 → `StaffCall.status`を'in_progress'に更新
3. 対応完了 → `StaffCall.status`を'resolved'に更新

### 5. セッション復帰フロー
1. 顧客がTelegram Mini Appsを再度開く（QRスキャンなし）
2. ローカルストレージに保存された`session_code`を確認
3. セッションが有効か確認
4. 「前回のセッション（テーブル: A-1）に戻りますか？」確認画面を表示
5. 「はい」→ セッションに復帰、メニュー一覧表示
6. 「いいえ」→ QRコードスキャン画面を表示

---

## データモデル設計のポイント

### 1. マルチユーザー対応
- 同一`Session`に複数の`Order`が紐づくことで、複数人が各自のスマホから同時注文可能
- `Order.telegram_user_id`で誰が注文したかを記録

### 2. 注文履歴の追跡
- `Order.order_number`でSession内の注文順序を管理
- 各`Order`は独立したステータスを持ち、調理進捗を個別管理

### 3. データの整合性
- `OrderItem`には注文時の商品名・価格をスナップショットとして保存
- メニュー変更後も過去の注文データに影響を与えない

### 4. ステータス管理
- `Order`と`OrderItem`の両方でステータス管理
- きめ細かい進捗管理とダッシュボード表示が可能

### 5. 会計の簡素化
- Sessionに対してPaymentは1対1
- テーブル単位の一括会計のみのため、複雑な割り勘ロジックは不要

### 6. 拡張性
- `Store`テーブルにより、将来的なマルチ店舗対応が可能
- `Category`による柔軟なメニュー分類

---

## 画像管理の仕様

### アップロード機能
1. **管理画面からのアップロード**
   - ブラウザの管理画面でメニュー編集時に画像をアップロード
   - ドラッグ&ドロップまたはファイル選択に対応
   - アップロード時にバリデーション（ファイルサイズ、フォーマット）を実施

2. **画像の自動処理**
   - オリジナル画像を保存（最大2MB、JPEG/PNG/WebP）
   - サムネイル画像を自動生成（400x300px）
   - 必要に応じて大サイズ画像も生成（800x600px）
   - 画像最適化（品質調整、メタデータ削除）

3. **保存先ディレクトリ構造**
   ```
   /media/
     └── menu_items/
         └── {store_id}/
             └── {menu_item_id}/
                 ├── original.jpg       # オリジナル画像
                 ├── thumbnail.jpg      # サムネイル（一覧用）
                 └── large.jpg          # 大サイズ（詳細用）
   ```

### 画像表示
1. **Telegram Mini Appsでの表示**
   - メニュー一覧：サムネイル画像を表示（400x300px）
   - メニュー詳細：大サイズ画像を表示（800x600px）
   - 遅延読み込み（Lazy Loading）でパフォーマンス最適化

2. **画像配信**
   - Djangoの静的ファイル配信機能を使用
   - 本番環境ではNginx等のWebサーバーで直接配信を推奨
   - キャッシュヘッダーを設定してブラウザキャッシュを活用

### セキュリティ
- アップロード可能なファイル形式を制限（JPEG, PNG, WebP）
- ファイルサイズ上限を設定（2MB）
- ファイル名をサニタイズ（セキュリティリスク排除）
- 画像のEXIF情報を削除（プライバシー保護）

---

## 注意事項

1. **売り切れ管理**：在庫管理機能は実装せず、`MenuItem.is_available`フラグを手動で変更
2. **QRコード**：`Table.qr_code_url`にはセッション開始用のユニークなURLを格納
3. **Telegram連携**：`Session.telegram_chat_id`と`Order.telegram_user_id`でTelegramユーザーを識別
4. **タイムゾーン**：すべての日時はUTCで保存し、表示時にローカルタイムに変換
5. **削除ポリシー**：論理削除（is_activeフラグ）を使用し、物理削除は行わない
6. **画像管理**：MenuItemImageテーブルで複数サイズの画像を管理、画像ファイルは/media/配下に保存
7. **セッション参加**：同一テーブルの既存アクティブセッションに自動参加
8. **注文キャンセル**：管理画面からのみ可能、顧客側からはキャンセル不可
9. **数量制限**：商品ごとに1回の注文での最大数量を設定（デフォルト10個）
