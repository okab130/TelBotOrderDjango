@echo off
REM Telegram Bot テスト環境セットアップスクリプト
REM Windows用

echo ================================================
echo   Telegram Bot テスト環境セットアップ
echo ================================================
echo.

REM 現在のディレクトリを確認
cd /d "%~dp0"
echo 作業ディレクトリ: %CD%
echo.

REM Step 1: 必要なパッケージのインストール
echo [1/6] 必要なパッケージをインストール中...
echo.
pip install python-telegram-bot==20.7 qrcode==7.4.2 pillow==10.1.0 python-dotenv==1.0.0 --quiet
if %ERRORLEVEL% NEQ 0 (
    echo エラー: パッケージのインストールに失敗しました
    pause
    exit /b 1
)
echo ✅ パッケージのインストール完了
echo.

REM Step 2: requirements.txt更新
echo [2/6] requirements.txt を更新中...
pip freeze > requirements.txt
echo ✅ requirements.txt 更新完了
echo.

REM Step 3: .envファイルの確認
echo [3/6] .env ファイルを確認中...
if not exist .env (
    echo .env ファイルが見つかりません。テンプレートを作成します...
    (
        echo # Django設定
        echo SECRET_KEY=your-secret-key-here-change-this-in-production
        echo DEBUG=True
        echo ALLOWED_HOSTS=localhost,127.0.0.1,*.ngrok-free.app
        echo.
        echo # Telegram Bot設定
        echo TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
        echo TELEGRAM_BOT_USERNAME=your_bot_username
        echo.
        echo # Webhook URL (ngrok起動後に更新)
        echo TELEGRAM_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app
        echo.
        echo # データベース
        echo DATABASE_URL=sqlite:///db.sqlite3
        echo.
        echo # その他
        echo TIME_ZONE=Asia/Tokyo
        echo LANGUAGE_CODE=ja
    ) > .env
    echo ✅ .env テンプレートを作成しました
    echo.
    echo ⚠️  重要: .env ファイルを編集して、以下の値を設定してください:
    echo    - TELEGRAM_BOT_TOKEN: BotFatherから取得したBot Token
    echo    - TELEGRAM_BOT_USERNAME: Botのユーザー名
    echo.
    echo 設定が完了したら、このスクリプトを再実行してください。
    pause
    exit /b 0
) else (
    echo ✅ .env ファイルが存在します
)
echo.

REM Step 4: telegram_botアプリの作成確認
echo [4/6] telegram_bot アプリを確認中...
if not exist telegram_bot (
    echo telegram_bot アプリを作成中...
    python manage.py startapp telegram_bot
    if %ERRORLEVEL% NEQ 0 (
        echo エラー: アプリの作成に失敗しました
        pause
        exit /b 1
    )
    echo ✅ telegram_bot アプリを作成しました
) else (
    echo ✅ telegram_bot アプリは既に存在します
)
echo.

REM Step 5: データベースマイグレーション
echo [5/6] データベースをマイグレーション中...
python manage.py makemigrations
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo エラー: マイグレーションに失敗しました
    pause
    exit /b 1
)
echo ✅ マイグレーション完了
echo.

REM Step 6: テストデータ作成
echo [6/6] テストデータを作成中...
python manage.py create_test_data
if %ERRORLEVEL% NEQ 0 (
    echo 警告: テストデータの作成に失敗しました（スキップ）
) else (
    echo ✅ テストデータ作成完了
)
echo.

REM 完了メッセージ
echo ================================================
echo   ✅ セットアップ完了！
echo ================================================
echo.
echo 次のステップ:
echo.
echo 1. ngrokをダウンロード・インストール:
echo    https://ngrok.com/download
echo.
echo 2. 2つのターミナルを開いて、以下を実行:
echo.
echo    [ターミナル1] Django開発サーバー起動:
echo    python manage.py runserver 0.0.0.0:8000
echo.
echo    [ターミナル2] ngrokトンネル起動:
echo    ngrok http 8000
echo.
echo 3. ngrokが表示するHTTPS URLを.envファイルの
echo    TELEGRAM_WEBHOOK_URL に設定
echo.
echo 4. Webhook設定:
echo    python manage.py set_telegram_webhook
echo.
echo 5. Telegram Botをテスト:
echo    - Botを検索
echo    - /start コマンド送信
echo.
echo 詳細は TELEGRAM_BOT_SETUP.md を参照してください。
echo.
pause
