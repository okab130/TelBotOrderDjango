# モックアップドキュメント

このディレクトリには、モバイルオーダーシステムの全画面のHTMLモックアップが含まれています。

## 📁 ディレクトリ構成

```
mockups/
├── index.html                    # モックアップ一覧（スタートページ）
├── assets/
│   └── style.css                 # 共通スタイルシート
├── customer/                     # 顧客向け画面（11画面）
│   ├── 01-qr-scan.html
│   ├── 02-party-size.html
│   ├── 03-session-resume.html
│   ├── 04-menu-list.html
│   ├── 06-cart.html
│   ├── 08-order-complete.html
│   ├── 09-order-history.html
│   ├── 10-payment-request.html
│   ├── 11-payment-complete.html
│   ├── 12-staff-call.html
│   └── 13-staff-call-complete.html
└── staff/                        # 店舗運用画面（5画面）
    ├── 01-cooking-dashboard.html
    ├── 02-payment-management.html
    ├── 03-menu-management.html
    ├── 04-menu-edit.html
    └── 05-sales-report.html
```

## 🚀 使用方法

### 1. モックアップを開く

ブラウザで `mockups/index.html` を開いてください：

```bash
# Windowsの場合
start mockups/index.html

# macOS/Linuxの場合
open mockups/index.html
# または
xdg-open mockups/index.html
```

### 2. 各画面を確認

インデックスページから各画面へのリンクをクリックして、実際のUI/UXを確認できます。

## 📱 顧客向け画面一覧

| 画面ID | ファイル名 | 画面名 | 説明 |
|--------|-----------|--------|------|
| CS-001 | 01-qr-scan.html | QRスキャン画面 | テーブルQRコード読み取り |
| CS-002 | 02-party-size.html | 来店人数入力画面 | セッション作成時の人数選択 |
| CS-003 | 03-session-resume.html | セッション復帰確認画面 | 既存セッション復帰確認 |
| CS-004 | 04-menu-list.html | メニュー一覧画面 | カテゴリ別メニュー表示 |
| CS-005 | （モーダル） | 商品詳細モーダル | 04-menu-list.html内に実装 |
| CS-006 | 06-cart.html | カート画面 | 注文前確認・編集 |
| CS-007 | （モーダル） | 注文確認モーダル | 06-cart.html内に実装 |
| CS-008 | 08-order-complete.html | 注文完了画面 | 注文完了メッセージ |
| CS-009 | 09-order-history.html | 注文履歴画面 | セッション内注文一覧 |
| CS-010 | 10-payment-request.html | 会計依頼画面 | 会計前合計確認 |
| CS-011 | 11-payment-complete.html | 会計依頼完了画面 | QRコードレシート表示 |
| CS-012 | 12-staff-call.html | 店員呼び出しモーダル | 理由選択と呼び出し |
| CS-013 | 13-staff-call-complete.html | 呼び出し完了画面 | 呼び出し完了メッセージ |

## 💼 店舗運用画面一覧

| 画面ID | ファイル名 | 画面名 | 説明 |
|--------|-----------|--------|------|
| SS-001 | 01-cooking-dashboard.html | 調理ダッシュボード | リアルタイム注文管理 |
| SS-002 | （モーダル） | 注文詳細モーダル | 01-cooking-dashboard.html内に実装 |
| SS-003 | 02-payment-management.html | 会計管理画面 | 会計依頼一覧と処理 |
| SS-004 | （モーダル） | 会計処理モーダル | 02-payment-management.html内に実装 |
| SS-005 | 03-menu-management.html | メニュー管理画面 | メニュー一覧と一括管理 |
| SS-006 | 04-menu-edit.html | メニュー編集画面 | 商品情報・画像編集 |
| SS-007 | 05-sales-report.html | 売上レポート画面 | 売上分析とエクスポート |

## 🎨 デザインシステム

### カラーパレット

モックアップは以下のカラーパレットを使用しています（`assets/style.css`に定義）：

**プライマリカラー**
- Primary: `#2196F3` (青)
- Primary Dark: `#1976D2`
- Primary Light: `#BBDEFB`

**セカンダリカラー**
- Secondary: `#FF9800` (オレンジ)
- Secondary Dark: `#F57C00`
- Secondary Light: `#FFE0B2`

**ステータスカラー**
- Success: `#4CAF50` (緑)
- Warning: `#FFC107` (黄)
- Error: `#F44336` (赤)
- Info: `#2196F3` (青)

### タイポグラフィ

- フォントファミリー: システムフォント（San Francisco, Roboto, Noto Sans JP）
- 基本フォントサイズ: 16px
- 見出しサイズ: H1 28px, H2 24px, H3 20px

### スペーシング

8pxベースのスペーシングシステム：
- XS: 4px
- S: 8px
- M: 16px
- L: 24px
- XL: 32px
- XXL: 48px

## ✨ インタラクティブ機能

モックアップには以下のインタラクティブ機能が実装されています：

### 顧客向け画面
- ✅ 人数増減ボタン（±ボタン）
- ✅ 数量選択（商品詳細モーダル、カート）
- ✅ モーダル開閉（商品詳細、注文確認、メニュー）
- ✅ 画面遷移リンク
- ✅ カート追加シミュレーション
- ✅ 自動画面遷移（呼び出し完了画面）

### 店舗運用画面
- ✅ タブ切り替え
- ✅ トグルスイッチ（自動更新、音声通知、売り切れ）
- ✅ モーダル開閉（注文詳細、会計処理）
- ✅ ドロップダウン選択（ステータス、カテゴリ）
- ✅ 検索ボックス
- ✅ 日付選択

## 📝 実装メモ

### モックアップの特徴

1. **レスポンシブデザイン**
   - モバイルファースト設計（顧客向け画面）
   - PC/タブレット対応（店舗運用画面）

2. **実際のデータ使用**
   - リアルな商品名・価格
   - 実際の業務フローに基づく画面遷移

3. **アクセシビリティ対応**
   - 最小タッチターゲット: 44x44px
   - コントラスト比考慮
   - セマンティックHTML

### 今後の実装に向けて

モックアップは以下の実装の基礎となります：

1. **Telegram Mini Apps実装**
   - HTMLをTelegram Web App形式に変換
   - Telegram WebApp API統合
   - バックエンドAPI接続

2. **Django管理画面カスタマイズ**
   - Django Adminテンプレートオーバーライド
   - カスタムビュー・URLの追加
   - WebSocket統合（リアルタイム更新）

3. **REST API開発**
   - モックアップのJavaScript部分をAPI呼び出しに置き換え
   - バリデーション実装
   - エラーハンドリング追加

## 🔧 カスタマイズ

### スタイル変更

`assets/style.css`を編集することで、全画面のスタイルを一括変更できます：

```css
/* 例: プライマリカラーを変更 */
:root {
  --primary: #2196F3;  /* この値を変更 */
}
```

### 新規画面追加

1. 適切なディレクトリ（customer/またはstaff/）にHTMLファイルを作成
2. `<link rel="stylesheet" href="../assets/style.css">`でスタイルシート読み込み
3. `index.html`にリンクを追加

## 📊 統計情報

- **総画面数**: 16画面（顧客11画面 + 店舗5画面）
- **総ファイル数**: 18ファイル（HTML: 17, CSS: 1）
- **総コード行数**: 約3,500行
- **対応ブラウザ**: Chrome, Firefox, Safari, Edge（モダンブラウザ）

## 🎯 使用用途

このモックアップは以下の用途で使用できます：

1. **UI/UXレビュー**: デザインと操作フローの確認
2. **顧客プレゼンテーション**: システムのデモンストレーション
3. **開発の参考資料**: 実装時のレイアウト・機能仕様の確認
4. **ユーザビリティテスト**: 実際のユーザーによる操作性評価

## 📞 フィードバック

モックアップに関するフィードバックや改善提案は、プロジェクトのIssueまたはPull Requestで受け付けています。

---

**作成日**: 2024-11-28  
**バージョン**: 1.0  
**ステータス**: 完成
