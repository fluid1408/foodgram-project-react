import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipe.models import Ingredients

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Загрузка данных из ingredients.csv'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(DATA_ROOT, options['filename']),
                newline='',
                encoding='utf8'
            ) as csv_file:
                data = csv.reader(csv_file)
                Ingredients.objects.bulk_create(
                    (Ingredients(
                        name=row[0],
                        measurement_unit=row[1])
                        for row in data),
                    batch_size=999
                )
        except FileNotFoundError:
            raise CommandError('Файл ingredients.csv не найден')
