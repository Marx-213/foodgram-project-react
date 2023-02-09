from django.contrib.auth import get_user_model
from django.db.models import Exists, F, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import StandardResultsSetPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    '''
    Вьюсет для работы с тегами.
    Добавлять теги может только админ.
    '''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    '''
    Вьюсет для работы с ингредиентами.
    Добавлять ингредиенты может только админ.
    '''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Вьюсет для работы с рецептами.
    Незарегистрованным пользователям разрешен только просмотр рецептов.
    '''
    queryset = Recipe.objects.prefetch_related(
        'tags',
        'ingredients',
    ).select_related('author')
    serializer_class = RecipeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        '''Делает подзапрос в модели Favorite и ShoppingCart.
        Аннотирует поля is_favorited и is_in_shopping_cart,
        и возвращает для них True или False,
        в зависимости от результата подзапроса.
        '''
        user = self.request.user
        if user.is_anonymous:
            user = 0
        favorite_recipes = Favorite.objects.filter(
            user=user,
            recipe=OuterRef('id')
        )
        shopping_cart = ShoppingCart.objects.filter(
            user=user,
            recipe=OuterRef('id')
        )
        queryset = Recipe.objects.annotate(
            is_favorited=Exists(favorite_recipes),
            is_in_shopping_cart=Exists(shopping_cart)
        )
        return queryset

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        '''
        Удаляет или записывает в Корзину покупок юзера и рецепт.
        Доступно только авторизованным пользователям.
        '''
        if request.method == 'DELETE':
            user = request.user
            result = get_object_or_404(ShoppingCart, user=user, recipe=pk)
            if result:
                result.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializers = ShoppingCartSerializer
        user = request.user
        if ShoppingCart.objects.filter(user=user, recipe=pk):
            return Response(
                {'errors': 'Рецепт уже в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        '''
        Удаляет или записывает в Избранное юзера и рецепт.
        Доступно только авторизованным пользователям.
        '''
        if request.method == 'DELETE':
            user = request.user
            result = get_object_or_404(Favorite, user=user, recipe=pk)
            if result:
                result.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializers = FavoriteSerializer
        user = request.user
        if Favorite.objects.filter(user=user, recipe=pk):
            return Response(
                {'errors': 'Рецепт уже в Избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        '''
        Получает ингредиенты из Корзины покупок пользователя,
        суммирует количество ингредиентов, и отправляет их в виде txt-файла.
        Доступно только авторизованным пользователям.
        '''
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = user.carts.select_related('user', 'recipe').values(
            ingredient=F('recipe__ingredients__name'),
            measurement_unit=F('recipe__ingredients__measurement_unit')
        ).annotate(amount=Sum('recipe__ingredients__ingredient__amount'))
        shopping_list = (
            f'Список покупок пользователя {user.username}\n'
        )
        for ingr in ingredients:
            shopping_list += (
                f'{ingr["ingredient"]}: '
                f'{ingr["amount"]} '
                f'{ingr["measurement_unit"]}\n'
            )
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
