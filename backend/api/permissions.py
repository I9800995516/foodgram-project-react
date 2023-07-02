from rest_framework.permissions import BasePermission


class IsSuperUserIsAdminIsModeratorIsAuthor(BasePermission):
    """
    Запросы PATCH и DELETE делает только
    суперпользователь Джанго, админ Джанго, пользователь
    с ролью admin или moderator, автор объекта.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'DELETE']:
            return (
                request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user.is_staff
                     or request.user.is_admin
                     or request.user.is_moderator
                     or request.user == obj.author)
            )
        return True

    def has_permission(self, request, view):
        return True


class IsRecipeAuthorOrReadOnly(BasePermission):
    """Только автор рецепта может его редактировать."""

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return (
                request.user.is_authenticated
                and obj.author == request.user
            )
        return True

    def has_permission(self, request, view):
        return True
