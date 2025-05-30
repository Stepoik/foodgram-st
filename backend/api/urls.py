from django.urls import path, include
from rest_framework import routers

from api.views.ingredient import IngredientViewSet
from api.views.receipt import RecipeViewSet
from api.views.user import UserViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
