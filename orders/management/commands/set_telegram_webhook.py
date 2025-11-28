"""
Telegram Webhook設定管理コマンド
"""
from django.core.management.base import BaseCommand
import asyncio
from orders.telegram_bot import telegram_bot


class Command(BaseCommand):
    help = 'Telegram BotのWebhookを設定します'

    def handle(self, *args, **options):
        self.stdout.write('Telegram Webhook設定中...')
        
        try:
            asyncio.run(telegram_bot.set_webhook())
            self.stdout.write(
                self.style.SUCCESS('✅ Webhook設定完了')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ エラー: {e}')
            )
