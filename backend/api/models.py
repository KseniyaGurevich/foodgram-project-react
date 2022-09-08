from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения'
    )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        null=True,
        verbose_name='Цвет',
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        unique=True,
        verbose_name='URL-ярлык',
    )

    def __str__(self):
        return f'{self.name} {self.id}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=30,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингрeдиенты',
        related_name='ingredients'
    )
    cooking_time = models.IntegerField(
        default=0,
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    is_favorited = models.BooleanField(
        verbose_name='В списке избанного',
        default=False,
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В списке покупок',
        default=False,
    )

    def __str__(self):
        return f'{self.name}, {self.author}'

    class Meta:
        ordering = ['pub_date']


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return (f'{self.recipe}'
                f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
                f' - {self.amount}')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()

    UniqueConstraint(fields=['user', 'recipe'], name='favorite_unique')

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_cart',
        verbose_name='Рецепт'
    )

    UniqueConstraint(fields=['user', 'recipe'], name='favorite_unique')

    def __str__(self):
        return f'{self.user} {self.recipe}'
