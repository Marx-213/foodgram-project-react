from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    '''Пермишен для тегов и ингредиентов.'''

    message = 'Вы не являетесь админом!'

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAuthorOrReadOnly(BasePermission):
    '''
    Изменить рецепт может только его автор.
    Все остальные не имеют доступа.
    '''

    message = 'Вы не являетесь автором рецепта!'

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            and request.user.is_authenticated
        )
