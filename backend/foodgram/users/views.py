from api.permissions import IsAdmin
from api.serializers import UserSerializer, PasswordSerializer
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from .models import User

class SignupViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        email = serializer.validated_data.get('email')

        send_mail(
            'Code for get token',
            'bestTeam@ever.com',
            [email],
            fail_silently=False,
        )
        return Response('serializer.data', status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    filter_backends = (filters.OrderingFilter,)

    @action(detail=False, methods=['get'])
    def me(self, request):
        self.kwargs['pk'] = request.user.pk
        return self.retrieve(request)


    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        user = get_object_or_404(User, username=request.user.username)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get('current_password')):
                return Response({'old_password': ['Wrong password.']}, 
                               status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                       status=status.HTTP_400_BAD_REQUEST)