from django_filters.rest_framework import FilterSet, BooleanFilter, NumberFilter, AllValuesMultipleFilter
from food.models import Recipe, Favorite, ShoppingCart


class RecipeFilter(FilterSet):
    author = NumberFilter(field_name='author__id')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset.exclude(favorited_by__user=user)

    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(in_carts__user=user)
        return queryset.exclude(in_carts__user=user)
