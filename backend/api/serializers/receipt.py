from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from food.models import (
    Recipe,
    Ingredient,
    RecipeIngredient
)
from .user import UserSerializer

TIME_MIN_VALUE = 1
TIME_MAX_VALUE = 32_000

INGREDIENT_AMOUNT_MIN_VALUE = 1
INGREDIENT_AMOUNT_MAX_VALUE = 32_000


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredient',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=obj).exists()
        return False


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=INGREDIENT_AMOUNT_MIN_VALUE,
        max_value=INGREDIENT_AMOUNT_MAX_VALUE
    )

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ингредиент не существует.")
        return value


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(
        min_value=TIME_MIN_VALUE,
        max_value=TIME_MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'image',
            'cooking_time', 'ingredients'
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Нужно указать хотя бы один ингредиент.")
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными.")
        return value

    def validate_image(self, value):
        if value in ("", None):
            raise serializers.ValidationError(
                "This field is required and cannot be empty.")
        return value

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            ) for item in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients is None:
            raise serializers.ValidationError("This field required.")
        if ingredients is not None:
            instance.recipe_ingredient.all().delete()
            self.create_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class RecipeLinkSerializer(serializers.Serializer):
    short_link = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {'short-link': data['short_link']}
