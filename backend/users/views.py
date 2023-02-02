from api.serializers import (PasswordSerializer, SubscribeSerializer,
                             UserSerializer)
from django.shortcuts import get_object_or_404
from recipes.models import Subscribe
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User


class UserViewSet(viewsets.ModelViewSet):
    '''Вьюсет для показа юзера'''
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    filter_backends = (filters.OrderingFilter,)

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        '''Показывает текущего юзера.'''
        self.kwargs['pk'] = request.user.pk
        return self.retrieve(request)

    @action(
        detail=False, methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        '''
        Проверяет введённый пароль с паролем из БД.
        Устанавливает новый пароль из сериализатора, если всё успешно.
        '''
        serializer = PasswordSerializer(data=request.data)
        user = get_object_or_404(User, username=request.user.username)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(serializer.data.get('old_password')):
            return Response(
                {'incorrect_password': ['Введите свой пароль еще раз.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response(
            {'status': 'Новый пароль успешно установлен!'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        '''
        Создает или удаляет подписку на пользователя.
        Перед этим проверяет подписку на наличие в БД и на то,
        чтобы пользователь не смог подписаться на самого себя.
        '''
        user = request.user
        author = get_object_or_404(User, id=pk)

        if request.method == 'DELETE':
            result = get_object_or_404(Subscribe, user=user, author=author)
            if not result:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            result.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = SubscribeSerializer
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscribe.objects.filter(user=user, author=author):
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {'user': user.id, 'author': pk}
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        '''Возвращает все подписки пользователя.'''
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
