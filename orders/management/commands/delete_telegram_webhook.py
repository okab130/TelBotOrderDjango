"""
Telegram Webhook削除管理コマンド
"""
from django.core.management.base import BaseCommand
import asyncio
from orders.telegram_bot import telegram_bot


class Command(BaseCommand):
    help = 'Telegram BotのWebhookを削除します'

    def handle(self, *args, **options):
        self.stdout.write('Telegram Webhook削除中...')
        
        try:
            asyncio.run(telegram_bot.delete_webhook())
            self.stdout.write(
                self.style.SUCCESS('✅ Webhook削除完了')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ エラー: {e}')
            )
