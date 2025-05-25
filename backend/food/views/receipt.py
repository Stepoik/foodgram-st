from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from food.filters.recipe_filter import RecipeFilter

from ..models import Recipe, Favorite, ShoppingCart
from food.permissions.author_permission import IsAuthorOrReadOnly
from ..serializers.receipt import (
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    RecipeShortSerializer,
    RecipeLinkSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    def get_queryset(self):
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticatedOrReadOnly])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeShortSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепт не найден в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticatedOrReadOnly])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, created = ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в корзине.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeShortSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепта нет в корзине.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=401)

        lines = []
        ingredients = {}
        for item in ShoppingCart.objects.filter(user=user):
            for ri in item.recipe.recipeingredient_set.all():
                name = ri.ingredient.name
                unit = ri.ingredient.measurement_unit
                key = f"{name} ({unit})"
                ingredients[key] = ingredients.get(key, 0) + ri.amount

        for name_unit, amount in ingredients.items():
            lines.append(f"{name_unit}: {amount}")

        response = Response('\n'.join(lines), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shopping_cart.txt'
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        link = request.build_absolute_uri(recipe.get_absolute_url())
        serializer = RecipeLinkSerializer({'short_link': link})
        return Response(serializer.data, status=status.HTTP_200_OK)
