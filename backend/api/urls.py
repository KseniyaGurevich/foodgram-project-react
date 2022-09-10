from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    ListSubscriptions, IsSubscribe)

router = DefaultRouter()


router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
#router.register(r'users/(?P<id>[^/.]+)/subscribe', IsSubscribeViewSet, basename='subscribe')

urlpatterns = [
    path(r'users/subscriptions/', ListSubscriptions.as_view()),
    path('users/<int:pk>/subscribe/', IsSubscribe.as_view()),
    path('', include(router.urls)),
    path(r'', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
