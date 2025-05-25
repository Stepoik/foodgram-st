# Foodgram

**Foodgram** — это веб-приложение для публикации и управления рецептами. Пользователи могут создавать рецепты, добавлять их в избранное, составлять список покупок и т.д.

## 🚀 Запуск проекта

### 1. Клонируйте репозиторий и перейдите в папку `infra`:

```bash
cd infra
```

### 2. Поднимите контейнеры с помощью Docker Compose:

```bash
docker compose build frontend
docker compose up backend
```

### 3. Выполните миграции:

```bash
docker exec -it foodgram-back python manage.py migrate
```

### 4. Загрузите список ингредиентов:

```bash
docker exec -it foodgram-back python manage.py load_ingredients food/data/ingredients.json
```

### 5. Загрузите пользователей:

```bash
docker exec -it foodgram-back python manage.py load_users_from_json food/data/users_data.json
```

### 6. Загрузите рецепты и изображения-заглушки:

```bash
docker exec -it foodgram-back python manage.py load_recipes_from_json food/data/recipes_data.json --image food/data/placeholder.jpg
```

### 7. Добавьте администратора:

```bash
docker exec -it foodgram-back python manage.py createsuperuser
```

## 🔗 Доступ к приложению

После запуска проект будет доступен по адресу:

```
http://localhost/
```

## 📦 Структура проекта

- `backend/` — Django-приложение
- `frontend/` — собранный фронтенд
- `infra/` — инфраструктура (docker-compose, nginx, настройки)
- `backend/food/data/` — JSON-файлы с тестовыми данными

## 🛠️ Зависимости

Убедитесь, что у вас установлены:

- Docker
- Docker Compose
