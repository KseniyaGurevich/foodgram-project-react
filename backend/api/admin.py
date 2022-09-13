from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)

admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author__username', 'author__email', 'name')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )
