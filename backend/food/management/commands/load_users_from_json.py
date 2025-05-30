import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает пользователей из JSON-файла. Пример: python manage.py load_users_from_json path/to/users_data.json'  # noqa

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str,
                            help='Путь к JSON-файлу с пользователями')

    def handle(self, *args, **options):
        json_path = options['json_path']
        try:
            with open(json_path, encoding='utf-8') as f:
                users = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"Ошибка при чтении файла: {e}"))
            return

        for user in users:
            if not User.objects.filter(username=user["username"]).exists():
                User.objects.create_user(
                    username=user["username"],
                    email=user["email"],
                    password=user["password"]
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Создан пользователь {user['username']}"))
            else:
                self.stdout.write(
                    f"Пользователь {user['username']} уже существует")
