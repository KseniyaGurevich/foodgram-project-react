from django_filters.rest_framework import FilterSet, filters

from .models import Recipe


class Filter(FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
