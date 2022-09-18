#import django_filters
from django_filters import filters

from .models import Recipe


class Filter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.CharFilter(field_name='tags__slug')
    is_favorited = filters.ChoiceFilter(
        choices=enumerate([0, 1]),
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=enumerate([0, 1]),
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
