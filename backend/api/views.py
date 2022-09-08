from django.db.models import Sum, Exists
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError

from .models import (Recipe, Tag, Ingredient, FavoriteRecipe,
                     ShoppingCart, IngredientRecipe)
from users.models import User, Follow
from .serializers import (RecipePostSerializer, RecipeGetSerializer,
                          TagSerializers, IngredientInRecipeSerializer,
                          IngredientSerializer, FavoriteRecipeSerializer,
                          ShortRecipeSerializer,
                          FollowSerializer)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import filters
from .filters import Filter

from rest_framework.mixins import CreateModelMixin

def adding_ingredients_to_recipe(self, recipe):
    ingredients_param = self.request.data.get("ingredients")
    for ingredient_param in ingredients_param:
        ingredient_id = ingredient_param.get("id")
        amount = ingredient_param.get("amount")
        if not Ingredient.objects.filter(id=ingredient_id).exists():
            raise ValidationError("Переданных ингредиентов нет в базе!")
        ingredientinrecipe, _ = IngredientRecipe.objects.get_or_create(
            ingredient_id=ingredient_id, amount=amount, recipe=recipe
        )


# def adding_ingredients_to_recipe(self, recipe):
#     ingredients_param = self.request.data.get("ingredients")
#     for ingredient_param in ingredients_param:
#         ingredient_id = ingredient_param.get("id")
#         amount = ingredient_param.get("amount")
#         if not Ingredient.objects.filter(id=ingredient_id).exists():
#             raise ValidationError("Переданных ингредиентов нет в базе!")
#         ingredientinrecipe, _ = IngredientRecipe.objects.get_or_create(
#             ingredient_id=ingredient_id, amount=amount, recipe=recipe
#         )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Filter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_authenticated:
    #         return Recipe.objects.annotate(
    #             is_favorited=Exists(
    #                 Favorite.objects.filter(user=user, recipe=OuterRef("id"))
    #             ),
    #             is_in_shopping_cart=Exists(
    #                 ShoppingCart.objects.filter(
    #                     user=user, recipe=OuterRef("id")
    #                 )
    #             ),
    #         ).select_related(
    #             "author",
    #         )
    #     return Recipe.objects.all()


    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     recipe_id = serializer.data.get('id')
    #     recipe = get_object_or_404(Recipe, pk=recipe_id)
    #     new_serializer = RecipeGetSerializer(
    #         recipe,
    #         context={'request': request}
    #     )
    #     return Response(new_serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe_id = serializer.data.get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        ingredients = self.request.data.pop('ingredients')
        for ingredient in ingredients:
            ingredient_id = ingredient.get("id")
            amount = ingredient.get("amount")
            ingredientinrecipe, _ = IngredientRecipe.objects.get_or_create(
                ingredient_id=ingredient_id,
                amount=amount,
                recipe=recipe
            )
        new_serializer = RecipeGetSerializer(
            recipe,
            context={'request': request}
        )
        serializer_post = RecipePostSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer_post.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        new_serializer = RecipeGetSerializer(
            recipe,
            context={'request': request},
        )
        return Response(new_serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        # recipe = serializer.save(author=self.request.user)
        # adding_ingredients_to_recipe(self, recipe)


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
                serializer = ShortRecipeSerializer(
                    recipe,
                    context={'request': request}
                )
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


# class FollowViewSet(viewsets.ModelViewSet):
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer
#
#     @action(
#         detail=False,
#         methods=['get'],
#         permission_classes=(IsAuthenticated,)
#     )
#     def subscriptions(self, request):
#         subs = Follow.objects.filter(user=request.user)
#         return Response(subs, status=status.HTTP_200_OK)
#
#     @action(
#         detail=True,
#         methods=['post', 'delete'],
#         permission_classes=(IsAuthenticated, )
#     )
#     def subscribe(self, request, pk):
#         author = get_object_or_404(User, pk=pk)
#         subscription = Follow.objects.filter(user=request.user, author=author)
#         if request.method == 'POST':
#             if subscription.exists():
#                 return Response(
#                     "Вы уже подписались на этого автора.",
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             elif author == request.user:
#                 return Response(
#                     "Нельзя подписаться на самого себя :)",
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             else:
#                 Follow.objects.create(user=request.user, author=author)
#                 serializer = FollowSerializer(author)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#         elif request.method == 'DELETE':
#             if subscription.exists():
#                 subscription.delete()
#                 return Response(
#                     'Вы успешно отписались от этого автора!',
#                     status=status.HTTP_204_NO_CONTENT
#                 )
#             else:
#                 return Response(
#                     'Вы ещё не подписаны на этого автора.',
#                     status.HTTP_400_BAD_REQUEST
#                 )

class SubscriptionsViewSet(viewsets.ViewSet):
    def get_permissions(self):
        permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def list(self, request):
        queryset = Follow.objects.filter(user=request.user)
        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeViewSet(viewsets.ViewSet):

    def get_permissions(self):
        permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def create(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        subscription = Follow.objects.filter(user=request.user, author=author)
        if subscription.exists():
            return Response(
                "Вы уже подписались на этого автора.",
                status=status.HTTP_400_BAD_REQUEST
            )
        elif author == request.user:
            return Response(
                "Нельзя подписаться на самого себя :)",
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            Follow.objects.create(user=request.user, author=author)
            serializer = FollowSerializer(author)
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