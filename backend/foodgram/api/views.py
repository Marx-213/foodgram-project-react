from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)


User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    '''
    Вьюсет для работы с тэгами.
    Добавлять теги может только админ.
    '''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = LimitOffsetPagination
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
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Вьюсет для работы с рецептами.
    Незарегистрованным пользователям разрешен только просмотр рецептов.
    '''

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ('name',)
    permission_classes = (IsAuthorOrReadOnly,)

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
        Получает рецепты из Корзины покупок и отправляет их в виде txt-файла.
        Доступно только авторизованным пользователям.
        '''
        user = request.user
        queryset = ShoppingCart.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = ShoppingCartSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        shopping_cart = f'{[recipe for recipe in serializer.data]}'
        filename = f'shopping_cart_{user}.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
