import mimetypes
from ipaddress import summarize_address_range

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ('name',)
    permission_classes = (IsAuthorOrReadOnly,)

    
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'DELETE':
                user = request.user
                recipe = get_object_or_404(Recipe, id=pk)
                result = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
                if result:
                    result.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(status=status.HTTP_400_BAD_REQUEST)

        serializers = ShoppingCartSerializer
        user = request.user
        if ShoppingCart.objects.filter(user=user, recipe=pk):
            return Response(
                {'errors': 'Товар уже в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'DELETE':
                user = request.user
                recipe = get_object_or_404(Recipe, id=pk)
                result = get_object_or_404(Favorite, user=user, recipe=recipe)
                if result:
                    result.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(status=status.HTTP_400_BAD_REQUEST)

        serializers = FavoriteSerializer
        user = request.user
        if Favorite.objects.filter(user=user, recipe=pk):
            return Response(
                {'errors': 'Товар уже в Избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
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