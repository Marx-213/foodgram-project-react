from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Укажите адрес электронной почты',
        unique=True,
        max_length=254,
    )
    username = models.TextField(
        verbose_name='Уникальный юзернейм',
        help_text='Укажите юзернейм',
        unique=True,
        max_length=150
    )
    first_name = models.CharField(
        verbose_name='Имя',
        help_text='Укажите ваше имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Укажите вашу фамилию',
        max_length=150
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text='Укажите ваш пароль',
        max_length=150
    )
    is_subscribed = models.ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribers',
        to='self',
        symmetrical='False',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username