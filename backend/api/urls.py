from django.urls import include, path
from rest_framework import routers
from users.views import UserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('users', UserViewSet, 'users')

urlpatterns = (
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('__debug__/', include('debug_toolbar.urls')),
)
