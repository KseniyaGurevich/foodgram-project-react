from django.contrib import admin

from .models import Tag, Recipe, Ingredient, IngredientRecipe, FavoriteRecipe, ShoppingCart

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author__username', 'author__email', 'name')