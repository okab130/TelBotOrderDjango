"""
Telegram Bot機能
"""
import os
import json
import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from django.conf import settings
from django.urls import reverse
from asgiref.sync import sync_to_async

from .models import Session, Table, Store, StaffCall

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram Bot管理クラス"""
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.webhook_url = settings.TELEGRAM_WEBHOOK_URL
        self.app = None
    
    async def initialize(self):
        """Botアプリケーションの初期化"""
        self.app = Application.builder().token(self.token).build()
        
        # コマンドハンドラー登録
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("menu", self.cmd_menu))
        self.app.add_handler(CommandHandler("order", self.cmd_order))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        
        # コールバックハンドラー登録
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("Telegram Botアプリケーション初期化完了")
    
    async def set_webhook(self):
        """Webhookの設定"""
        if not self.app:
            await self.initialize()
        
        webhook_url = f"{self.webhook_url}/api/telegram/webhook/"
        await self.app.bot.set_webhook(webhook_url)
        logger.info(f"Webhook設定完了: {webhook_url}")
    
    async def delete_webhook(self):
        """Webhookの削除"""
        if not self.app:
            await self.initialize()
        
        await self.app.bot.delete_webhook()
        logger.info("Webhook削除完了")
    
    async def process_update(self, update_data: dict):
        """Webhookからのアップデート処理"""
        if not self.app:
            await self.initialize()
        
        update = Update.de_json(update_data, self.app.bot)
        await self.app.process_update(update)
    
    # コマンドハンドラー
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /start コマンド
        ボットの初回起動時に実行される
        """
        user = update.effective_user
        
        # WebApp URLを取得
        webapp_url = f"{settings.TELEGRAM_WEBHOOK_URL}/miniapp/"
        
        # インラインキーボード作成
        keyboard = [
            [InlineKeyboardButton(
                "🍽️ 注文を開始", 
                web_app=WebAppInfo(url=webapp_url)
            )],
            [InlineKeyboardButton("ℹ️ ヘルプ", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
👋 こんにちは、{user.first_name}さん！

モバイルオーダーシステムへようこそ🎉

**ご利用方法:**
1️⃣ テーブルのQRコードをスキャン
2️⃣ メニューから商品を選択
3️⃣ 注文を確定

複数人で同時に注文できます！
"""
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /help コマンド
        ヘルプメッセージを表示
        """
        help_text = """
📖 **モバイルオーダーシステム ヘルプ**

**基本の使い方:**
• テーブルのQRコードをスキャンして注文開始
• メニューから商品を選択
• 数量を決めて注文確定

**便利な機能:**
• 複数人が同時に注文可能
• 追加注文も簡単
• 注文履歴の確認
• 店員呼び出し

**コマンド一覧:**
/start - ボット起動
/help - ヘルプ表示
/menu - メニュー表示
/order - 注文履歴
/status - 注文状況確認

**お困りの場合:**
店員呼び出しボタンから
お気軽にお声がけください 🙋
"""
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
    
    async def cmd_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /menu コマンド
        メニューへのリンクを表示
        """
        webapp_url = f"{settings.TELEGRAM_WEBHOOK_URL}/miniapp/"
        
        keyboard = [
            [InlineKeyboardButton(
                "🍽️ メニューを見る", 
                web_app=WebAppInfo(url=webapp_url)
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "メニューを表示します 📋",
            reply_markup=reply_markup
        )
    
    async def cmd_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /order コマンド
        注文履歴を表示
        """
        user_id = str(update.effective_user.id)
        
        # セッション取得（非同期）
        session = await self._get_active_session(user_id)
        
        if not session:
            await update.message.reply_text(
                "アクティブなセッションがありません。\n"
                "QRコードをスキャンして注文を開始してください。"
            )
            return
        
        # 注文履歴取得
        orders = await self._get_session_orders(session)
        
        if not orders:
            await update.message.reply_text(
                "まだ注文がありません。\n"
                "メニューから商品を選んでください。"
            )
            return
        
        # 注文履歴テキスト生成
        order_text = f"📋 **注文履歴** (テーブル: {session.table.table_number})\n\n"
        
        total = 0
        for order in orders:
            status_emoji = {
                'pending': '⏳',
                'cooking': '👨‍🍳',
                'ready': '✅',
                'served': '🍽️',
                'cancelled': '❌'
            }.get(order.status, '❓')
            
            order_text += f"{status_emoji} **注文 #{order.order_number}**\n"
            order_text += f"金額: ¥{order.total_amount:,.0f}\n"
            order_text += f"状態: {order.get_status_display()}\n\n"
            
            if order.status != 'cancelled':
                total += order.total_amount
        
        order_text += f"**合計: ¥{total:,.0f}**"
        
        await update.message.reply_text(
            order_text,
            parse_mode='Markdown'
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /status コマンド
        現在の注文状況を表示
        """
        user_id = str(update.effective_user.id)
        
        # セッション取得
        session = await self._get_active_session(user_id)
        
        if not session:
            await update.message.reply_text(
                "アクティブなセッションがありません。"
            )
            return
        
        # 未提供の注文取得
        pending_orders = await self._get_pending_orders(session)
        
        if not pending_orders:
            await update.message.reply_text(
                "すべての注文が提供済みです ✅"
            )
            return
        
        status_text = "📊 **注文状況**\n\n"
        
        for order in pending_orders:
            status_emoji = {
                'pending': '⏳ 受付済み',
                'cooking': '👨‍🍳 調理中',
                'ready': '✅ 調理完了'
            }.get(order.status, order.status)
            
            status_text += f"注文 #{order.order_number}: {status_emoji}\n"
        
        await update.message.reply_text(
            status_text,
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """コールバッククエリハンドラー"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "help":
            await self.cmd_help(update, context)
        elif query.data == "menu":
            await self.cmd_menu(update, context)
        elif query.data == "order":
            await self.cmd_order(update, context)
    
    # ヘルパーメソッド（非同期データベースアクセス）
    
    @sync_to_async
    def _get_active_session(self, telegram_user_id: str) -> Optional[Session]:
        """アクティブなセッションを取得"""
        try:
            return Session.objects.filter(
                telegram_chat_id=telegram_user_id,
                status__in=['active', 'calling_staff', 'payment_requested']
            ).select_related('table').first()
        except Session.DoesNotExist:
            return None
    
    @sync_to_async
    def _get_session_orders(self, session: Session):
        """セッションの全注文を取得"""
        return list(
            session.order_set.all()
            .exclude(status='cancelled')
            .order_by('-ordered_at')
        )
    
    @sync_to_async
    def _get_pending_orders(self, session: Session):
        """未提供の注文を取得"""
        return list(
            session.order_set.filter(
                status__in=['pending', 'cooking', 'ready']
            ).order_by('ordered_at')
        )


# グローバルインスタンス
telegram_bot = TelegramBot()


async def send_notification(chat_id: str, message: str):
    """
    通知メッセージを送信
    
    Args:
        chat_id: TelegramチャットID
        message: 送信するメッセージ
    """
    if not telegram_bot.app:
        await telegram_bot.initialize()
    
    try:
        await telegram_bot.app.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"通知送信エラー: {e}")


async def send_order_notification(order):
    """
    注文通知を送信
    
    Args:
        order: Orderモデルインスタンス
    """
    session = order.session
    if not session.telegram_chat_id:
        return
    
    items_text = "\n".join([
        f"• {item.menu_item_name} x{item.quantity}"
        for item in order.orderitem_set.all()
    ])
    
    message = f"""
🔔 **新規注文**

テーブル: {session.table.table_number}
注文番号: #{order.order_number}

{items_text}

合計: ¥{order.total_amount:,.0f}
"""
    
    await send_notification(session.telegram_chat_id, message)


async def send_staff_call_notification(staff_call):
    """
    店員呼び出し通知を送信
    
    Args:
        staff_call: StaffCallモデルインスタンス
    """
    session = staff_call.session
    
    reason_text = {
        'water': '💧 お水',
        'payment': '💳 会計',
        'question': '❓ 質問',
        'complaint': '⚠️ 苦情',
        'other': '📝 その他'
    }.get(staff_call.reason, staff_call.reason)
    
    message = f"""
🔔 **店員呼び出し**

テーブル: {session.table.table_number}
理由: {reason_text}

{staff_call.message if staff_call.message else ''}
"""
    
    # 店舗の通知先チャットIDに送信（設定が必要）
    # ここでは実装省略
    logger.info(f"店員呼び出し通知: {message}")
