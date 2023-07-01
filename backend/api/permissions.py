from rest_framework import permissions


class IsSuperUserIsAdminIsModeratorIsAuthor(permissions.BasePermission):
    """
    Запросы PATCH и DELETE делает только
    суперпользователь Джанго, админ Джанго, пользователь
    с ролью admin или moderator, автор объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_staff
                 or request.user.is_admin
                 or request.user.is_moderator
                 or request.user == obj.author)
        )


class IsRecipeAuthorOrReadOnly(permissions.BasePermission):
    """Только авто редактирует рецепт."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and obj.author == request.user)
