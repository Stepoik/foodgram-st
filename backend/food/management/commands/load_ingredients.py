import json
from django.core.management.base import BaseCommand
from food.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузить ингредиенты из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str,
                            help='Путь до JSON-файла с ингредиентами')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for item in data:
            obj, created = Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Успешно загружено {count} ингредиентов'))
