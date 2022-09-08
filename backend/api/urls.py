from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    SubscriptionsViewSet, SubscribeViewSet)

router = DefaultRouter()


router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users/subscriptions', SubscriptionsViewSet, basename='subscriptions')
router.register(r'users/(?P<id>[^/.]+)/subscribe', SubscribeViewSet, basename='subscribe')

urlpatterns = [
    path('', include(router.urls)),
    path(r'', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
