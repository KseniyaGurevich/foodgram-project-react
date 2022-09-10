from django.db.models import Sum, Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin

from .models import (Recipe, Tag, Ingredient, FavoriteRecipe,
                     ShoppingCart, IngredientRecipe)
from users.models import User, Follow
from .serializers import (RecipePostSerializer, RecipeGetSerializer,
                          TagSerializers, IngredientInRecipeSerializer,
                          IngredientSerializer, FavoriteRecipeSerializer,
                          ShortRecipeSerializer, FollowSerializer)
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import filters
from .filters import Filter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Filter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        ingredients = self.request.data.pop('ingredients')
        for ingredient in ingredients:
            ingredient_id = ingredient.get("id")
            amount = ingredient.get("amount")
            ingredientrecipe, _ = IngredientRecipe.objects.get_or_create(
                ingredient_id=ingredient_id,
                amount=amount,
                recipe=recipe
            )
        new_serializer = RecipeGetSerializer(
            recipe,
            context={'request': request}
        )
        return Response(new_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        ingredients = self.request.data.pop('ingredients')
        for ingredient in ingredients:
            ingredient_id = ingredient.get("id")
            amount = ingredient.get("amount")
            ingredientrecipe, _ = IngredientRecipe.objects.get_or_create(
                ingredient_id=ingredient_id,
                amount=amount,
                recipe=recipe
            )
        new_serializer = RecipeGetSerializer(
            recipe,
            context={'request': request},
            partial=partial
        )
        return Response(new_serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, ),
    )
    def download_shopping_cart(self, request):
        ingredient_list = IngredientRecipe.objects.filter(
            recipe__recipe_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount'))
        shopping_list = [
            f'Cписок покупок:\n'
            f'\n'
        ]
        shopping_list += '\n'.join([
            f'{ingredient["ingredient__name"]}'
            f'({ingredient["ingredient__measurement_unit"]}) - '
            f'{ingredient["sum_amount"]}'
            for ingredient in ingredient_list
        ])
        filename = f'shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_shopping_cart = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if request.method == "POST":
            if recipe_in_shopping_cart.exists():
                return Response(
                    "Этот рецепт уже есть в списке покупок",
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer = ShortRecipeSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if recipe_in_shopping_cart.exists():
                recipe_in_shopping_cart.delete()
                return Response(
                    'Рецепт успешно удалён из списка покупок',
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    'Рецепт нельзя удалить, его нет в списке покупок',
                    status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if request.method == 'POST':
            if recipe_in_favorite.exists():
                return Response("Этот рецепт уже есть в избранном",
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
                serializer = ShortRecipeSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if recipe_in_favorite.exists():
                recipe_in_favorite.delete()
                return Response('Рецепт успешно удалён из избранного',
                                status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    'Этот рецепт нельзя удалить, его нет в избранном',
                    status.HTTP_400_BAD_REQUEST
                )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    #permission_classes = (IsAdminOrReadOnly, )
    serializer_class = TagSerializers
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)
    pagination_class = None


# class SubscriptionsViewSet(viewsets.ViewSet):
#     def get_permissions(self):
#         permission_classes = (IsAuthenticated,)
#         return [permission() for permission in permission_classes]
#
#     def list(self, request):
#         queryset = Follow.objects.filter(user=request.user)
#         serializer = FollowSerializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class ListSubscriptions(APIView):
    def get_permissions(self):
        permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def get(self, request):
        user = request.user
        list_author = Follow.objects.filter(user=request.user)
        serializer = FollowSerializer(
            list_author,
            context={'request': request},
            many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class IsSubscribe(APIView):
    def get_permissions(self):
        permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        is_subscribed = Follow.objects.filter(user=request.user, author=author)
        if author == request.user:
            return Response("Нельзя подписаться на самого себя",
                            status=status.HTTP_400_BAD_REQUEST)
        elif is_subscribed.exists():
            return Response(
                "Вы уже подписались на этого автора.",
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            q = Follow.objects.create(user=request.user, author=author)
            serializer = FollowSerializer(
                author,
                #context={'request': 'request'}
            )
            print('********')
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        subscription = Follow.objects.filter(user=request.user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(
                'Вы успешно отписались от этого автора!',
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                'Вы ещё не подписаны на этого автора.',
                status.HTTP_400_BAD_REQUEST
            )