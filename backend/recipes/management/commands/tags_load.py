import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Tag

CSV_DATA = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    '''Добавляет теги из CSV файла  в Postqresql.'''

    help = 'uploading tags from csv in db'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='tags.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(CSV_DATA, options['filename']), 'r',
                encoding='utf-8'
            ) as data:
                tags = csv.reader(data)
                for tag in tags:
                    Tag.objects.get_or_create(
                        name=tag[0],
                        color=tag[1],
                        slug=tag[2]
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        'The database was successfully filled with tags'
                    )
                )
        except FileNotFoundError:
            raise CommandError('Не удается найти файл tags.csv')
