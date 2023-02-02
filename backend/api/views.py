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
from django.db.models import Sum
from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from django.db.models import F, Exists, OuterRef


User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    '''
    Вьюсет для работы с тегами.
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
    queryset = Recipe.objects.prefetch_related(
        'tags',
        'ingredients',
    ).select_related('author')
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ('name',)
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            favorite_recipes = Favorite.objects.filter(
                user=user,
                recipe=OuterRef('id')
            )
            queryset2 = queryset.filter(
                Exists(favorite_recipes)
            )
            a = super().get_serializer(queryset2)
            print(a.data)
            print(queryset2, 'queryset2')
        else:
            queryset2 = queryset.all()
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
