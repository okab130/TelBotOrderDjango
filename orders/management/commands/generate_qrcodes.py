"""
QRコード生成管理コマンド
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import qrcode
from pathlib import Path
from orders.models import Table


class Command(BaseCommand):
    help = 'テーブル用QRコードを生成します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--table-id',
            type=int,
            help='特定のテーブルIDのみ生成'
        )

    def handle(self, *args, **options):
        table_id = options.get('table_id')
        
        if table_id:
            tables = Table.objects.filter(id=table_id)
        else:
            tables = Table.objects.all()
        
        if not tables.exists():
            self.stdout.write(
                self.style.WARNING('テーブルが見つかりません')
            )
            return
        
        # QRコード保存先ディレクトリ作成
        qr_dir = Path(settings.MEDIA_ROOT) / 'qrcodes'
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        for table in tables:
            # QRコードのURLを生成
            qr_url = f"{settings.TELEGRAM_WEBHOOK_URL}/miniapp/?table_id={table.id}"
            
            # QRコード生成
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 保存
            filename = f"table_{table.id}_{table.table_number}.png"
            filepath = qr_dir / filename
            img.save(filepath)
            
            # テーブルのqr_code_urlを更新
            table.qr_code_url = qr_url
            table.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ テーブル {table.table_number}: {filepath}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {tables.count()}個のQRコードを生成しました'
            )
        )
