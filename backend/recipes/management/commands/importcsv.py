import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def get_reader(file_name: str):
    csv_path = os.path.join(settings.BASE_DIR, 'data/', file_name)
    with open(csv_path, 'r', encoding='utf-8', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        return list(reader)


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Началась загрузка данных.'))

        try:
            csv_reader = get_reader('ingredients.csv')
            rows = list(csv_reader)
            for i, row in enumerate(rows, start=1):
                if len(row) != 2:
                    self.stderr.write(
                        self.style.WARNING(
                            f'Некорректная строка CSV в строке {i}: {row}',
                        ),
                    )
                    continue

                name = row[0]
                measurement_unit = row[1]
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                )
                ingredient.measurement_unit = measurement_unit
                ingredient.save()

            self.stdout.write(self.style.SUCCESS('Загрузка данных завершена.'))
        except (FileNotFoundError, PermissionError) as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка при открытии файла: {e}'),
            )
        except csv.Error as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка при чтении CSV: {e}'),
            )
