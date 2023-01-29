from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        'pk',
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )
    list_filter = (
        'username',
        'email',
    )


admin.site.register(User, CustomUserAdmin)
