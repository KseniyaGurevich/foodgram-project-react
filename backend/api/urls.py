from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, IsSubscribe, ListSubscriptions,
                    RecipeViewSet, TagViewSet)

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(r'users/subscriptions/', ListSubscriptions.as_view()),
    path('users/<int:pk>/subscribe/', IsSubscribe.as_view()),
    path('', include(router.urls)),
    path(r'', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
