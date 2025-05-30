import json
import random
from pathlib import Path
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from food.models import Recipe, Ingredient, RecipeIngredient
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает рецепты из JSON и добавляет случайные ингредиенты (ID 1–2000)'

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str,
                            help='Путь к JSON-файлу с рецептами')
        parser.add_argument(
            '--image', type=str, required=False,
            help='Путь к картинке-заглушке, которая будет использоваться для всех рецептов'
        )

    def handle(self, *args, **options):
        json_path = Path(options['json_path'])
        image_path = Path(options['image']) if options.get('image') else None

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f"Файл {json_path} не найден"))
            return

        if image_path and not image_path.exists():
            self.stderr.write(self.style.ERROR(
                f"Файл изображения {image_path} не найден"))
            return

        with json_path.open(encoding='utf-8') as f:
            recipes = json.load(f)

        ingredient_ids = list(
            Ingredient.objects.filter(id__range=(
                1, 2000)).values_list('id', flat=True)
        )
        if not ingredient_ids:
            self.stderr.write(self.style.ERROR(
                "Не найдены ингредиенты с ID 1–2000."))
            return

        for data in recipes:
            try:
                author = User.objects.get(username=data["author"])
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f"Автор {data['author']} не найден"))
                continue

            recipe = Recipe.objects.create(
                name=data["name"],
                author=author,
                text=data.get(
                    "description", "Автоматически сгенерированное описание."),
                cooking_time=data["cooking_time"],
            )

            # Привязка изображения
            if image_path:
                with image_path.open('rb') as img_file:
                    recipe.image.save(
                        image_path.name, ImageFile(img_file), save=True)
            else:
                # Если не указан путь к картинке — можно скипнуть или задать через FileField с заглушкой
                self.stderr.write(
                    f"⛔ Нет изображения для рецепта {recipe.name}, добавьте через --image")

            # Добавим 3–6 случайных ингредиентов
            selected_ids = random.sample(
                ingredient_ids, k=random.randint(3, 6))
            for ing_id in selected_ids:
                amount = random.randint(10, 300)
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient_id=ing_id,
                    amount=amount
                )

            self.stdout.write(
                self.style.SUCCESS(f"✅ Рецепт '{recipe.name}' создан с {len(selected_ids)} ингредиентами"))
