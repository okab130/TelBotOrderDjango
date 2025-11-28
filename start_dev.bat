@echo off
REM 開発環境起動スクリプト
REM Djangoサーバーとngrokを同時起動

echo ================================================
echo   モバイルオーダーシステム 開発環境起動
echo ================================================
echo.

REM 現在のディレクトリに移動
cd /d "%~dp0"

echo [1/2] Django開発サーバーを起動中...
start "Django Server" cmd /k "python manage.py runserver 0.0.0.0:8000"

REM Djangoサーバーの起動を待つ
timeout /t 3 /nobreak > nul

echo [2/2] ngrokトンネルを起動中...
start "ngrok Tunnel" cmd /k "ngrok http 8000"

echo.
echo ✅ 起動完了！
echo.
echo ================================================
echo   次のステップ
echo ================================================
echo.
echo 1. ngrokウィンドウでHTTPS URLを確認
echo    例: https://abc123.ngrok-free.app
echo.
echo 2. .env ファイルを開き、TELEGRAM_WEBHOOK_URL を更新:
echo    TELEGRAM_WEBHOOK_URL=https://abc123.ngrok-free.app
echo.
echo 3. 新しいターミナルで Webhook を設定:
echo    python manage.py set_telegram_webhook
echo.
echo 4. Telegram Botにアクセスしてテスト:
echo    - /start コマンドを送信
echo    - QRコードをスキャン (管理画面で生成)
echo.
echo 管理画面: http://localhost:8000/admin/
echo API: http://localhost:8000/api/
echo ngrok Dashboard: http://127.0.0.1:4040
echo.
echo ================================================
echo.
pause
