import django_filters

from .models import Recipe


class Filter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
