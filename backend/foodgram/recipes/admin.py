from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Subscribe, Tag, TagRecipe)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    '''Админка для тегов.'''

    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_display_links = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    ordering = ('color',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''Админка для ингредиентов.'''

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_display_links = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (' name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''Админка для рецептов.'''

    list_display = (
        'id',
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'favorites_count'
    )
    list_display_links = (
        'id',
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'favorites_count'
    )
    list_filter = ('name', 'author', 'tags',)

    def favorites_count(self, obj):
        '''
        Выводит общее число добавлений конкретного рецепта(obj) в Избранное.
        '''
        return obj.user_favorites.count()


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    '''Админка для связанных тегов и рецептов.'''

    list_display = (
        'recipe',
        'tag',
    )
    list_display_links = (
        'recipe',
        'tag',
    )


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    '''Админка для связанных ингредиентов и рецептов.'''

    list_display = (
        'recipe',
        'amount',
        'ingredients',
    )
    list_display_links = (
        'recipe',
        'amount',
        'ingredients',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    '''Админка для Корзины покупок.'''

    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    '''Админка для подписок.'''

    list_display = ('user', 'author')
    list_display_links = ('user', 'author')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    '''Админка для Избранного.'''

    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
