from django.urls import include, path, re_path
from rest_framework.authtoken import views

from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, IngredientViewSet

router = DefaultRouter()


router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(r'', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
