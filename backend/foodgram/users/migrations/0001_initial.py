# Generated by Django 2.2.19 on 2023-01-24 10:16

import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(help_text='Укажите адрес электронной почты', max_length=254, unique=True, verbose_name='Адрес электронной почты')),
                ('username', models.TextField(help_text='Укажите юзернейм', max_length=150, unique=True, verbose_name='Уникальный юзернейм')),
                ('first_name', models.CharField(help_text='Укажите ваше имя', max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(help_text='Укажите вашу фамилию', max_length=150, verbose_name='Фамилия')),
                ('password', models.CharField(help_text='Укажите ваш пароль', max_length=150, verbose_name='Пароль')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('is_subscribed', models.ManyToManyField(related_name='_user_is_subscribed_+', to=settings.AUTH_USER_MODEL, verbose_name='Подписка')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('username',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
