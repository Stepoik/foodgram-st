from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from food.models import Ingredient
from food.serializers.ingredient import IngredientSerializer
from food.filters.name_search_filter import NameSearchFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [NameSearchFilter]
    search_fields = ['^name']
