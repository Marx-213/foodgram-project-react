from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    '''
    Фильтрация по избранному, автору, списку покупок и тегам.
    '''

    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        '''Показывает только рецепты, находящиеся в списке Избранного.'''
        if self.request.user.is_anonymous:
            return queryset
        if value is False:
            return queryset.exclude(user_favorites__user=self.request.user.id)
        return queryset.filter(user_favorites__user=self.request.user.id)

    def get_is_in_shopping_cart(self, queryset, name, value):
        '''Показывает только рецепты, находящиеся в списке покупок.'''
        if self.request.user.is_anonymous:
            return queryset
        if value is False:
            return queryset.exclude(carts__user=self.request.user.id)
        return queryset.filter(carts__user=self.request.user.id)
