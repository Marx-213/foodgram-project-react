import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient

CSV_DATA = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    '''Добавляет ингредиенты из CSV файла  в Postqresql.'''

    help = 'uploading ingredients from csv in db'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='ingredients.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(CSV_DATA, options['filename']), 'r',
                encoding='utf-8'
            ) as data:

                ingredients = csv.reader(data)
                for ingredient in ingredients:
                    name, measurement_unit = ingredient
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        'The database was successfully filled with ingredients'
                    )
                )
        except FileNotFoundError:
            raise CommandError('Не удается найти файл ingredients.csv')
