from api.serializers import (PasswordSerializer, SubscribeSerializer,
                             UserSerializer, UserSubscribeSerializer)
from django.shortcuts import get_object_or_404
from recipes.models import Subscribe
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    filter_backends = (filters.OrderingFilter,)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def me(self, request):
        queryset = User.objects.filter(id=request.user.id)
        serializer = UserSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data[0])


    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        user = get_object_or_404(User, username=request.user.username)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get('current_password')):
                return Response({'incorrect_password': ['Введите свой пароль еще раз.']}, 
                               status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'status': 'Новый пароль успешно установлен!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                       status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        if request.method == 'DELETE':
            user = request.user
            author = get_object_or_404(User, id=pk)
            result = get_object_or_404(Subscribe, user=user, author=author)
            if result:
                result.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscribeSerializer
        user = request.user
        author = get_object_or_404(User, id=pk)
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


    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
