from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

COOKING_TIME_MIN_VALUE = 1
COOKING_TIME_MAX_VALUE = 32_000

INGREDIENT_AMOUNT_MIN_VALUE = 1
INGREDIENT_AMOUNT_MAX_VALUE = 32_000


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Почта')
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        blank=True,
        verbose_name='Аватарка'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.PositiveSmallIntegerField(
        help_text="Время приготовления в минутах",
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN_VALUE,
                message='Минимальное время — 1 минута.'
            ),
            MaxValueValidator(
                COOKING_TIME_MAX_VALUE,
                message='Максимальное время — 32000 минут (~500 часов).'
            )
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes-detail', kwargs={'pk': self.pk})


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                INGREDIENT_AMOUNT_MIN_VALUE,
                message='Минимальное количество — 1'
            ),
            MaxValueValidator(
                INGREDIENT_AMOUNT_MAX_VALUE,
                message='Максимальное количество — 32000'
            )
        ]
    )

    class Meta:
        ordering = ['recipe__name', 'ingredient__name']
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f"{self.amount} {self.ingredient.measurement_unit} {self.ingredient.name}"  # noqa


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-id']
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f"{self.user.email} добавил в избранное {self.recipe.name}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-id']
        unique_together = ('user', 'recipe')
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return f"{self.user.email} добавил в корзину {self.recipe.name}"


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ['-id']
        unique_together = ('subscriber', 'target')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.subscriber.email} подписан на {self.target.email}"
