from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import serializers

from .models import Recipe, Tag, Ingredient, IngredientRecipe
from users.models import User, Follow
from users.serializers import CurrentUserSerializer
import base64
from django.core.files.base import ContentFile
import webcolors


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializers(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        ingredients = IngredientRecipe.objects.filter(ingredient_id=obj.id)
        for ingredient in ingredients:
            return ingredient.amount

    # def get_amount(self, obj):
    #     return obj.ingredient.all().values_list('amount')[0][0]


class AmountSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def get_amount(self, obj):
        ingredients = IngredientRecipe.objects.filter(ingredient_id=obj.id)
        for ingredient in ingredients:
            return ingredient.amount

    # def get_amount(self, obj):
    #     return obj.ingredient.all().values_list('amount')[0][0]


class RecipePostSerializer(serializers.ModelSerializer):
    author = CurrentUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AmountSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления не может занимать меньше минуты'
        ),)
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            tags_id = tag.id
            recipe.tags.add(get_object_or_404(Tag, pk=tags_id))
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount']
                )
        for tag in tags:
            tags_id = tag.id
            instance.tags.add(get_object_or_404(Tag, pk=tags_id))
        return super().update(instance, validated_data)


class RecipeGetSerializer(serializers.ModelSerializer):
    author = CurrentUserSerializer(read_only=True)
    tags = TagSerializers(read_only=True, many=True)
    ingredients = IngredientInRecipeSerializer(read_only=True, many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'recipe')

    def get_recipe(self, obj):
        recipe = obj.recipes.all()
        return FavoriteRecipeSerializer(recipe, many=True).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    # def validated_following(self, user):
    #     if user == self.context.get('request').user:
    #         raise serializers.ValidationError("Нельзя подписаться на самого себя ;)")
    #     return user

    class Meta:
        model = Follow
        fields = '__all__'

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj.author).exsist()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()




