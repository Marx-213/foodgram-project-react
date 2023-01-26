from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    """
    Фильтрация по избранному, автору, списку покупок и тегам.
    """
    author = filters.AllValuesMultipleFilter(field_name='author__username')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(user_favorites__user=self.request.user.id)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(carts__user=self.request.user)
