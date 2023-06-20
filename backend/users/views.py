from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow, User
<<<<<<< HEAD
from .serializers import (AddFollowerSerializer, GetFollowSerializer,
                          UniqueUserCreateSerializer)
=======
from .serializers import (
    GetFollowSerializer,
    AddFollowerSerializer,
    CustomUserCreateSerializer,
)
>>>>>>> master


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
<<<<<<< HEAD
            return UniqueUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UniqueUserCreateSerializer
=======
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return CustomUserCreateSerializer
>>>>>>> master

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        authentication_classes=(TokenAuthentication),
    )
    def follow(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        subscription = Follow.objects.filter(
            user=user,
            author=author,
        )

        if request.method == 'POST':
            serializer = AddFollowerSerializer(
                author,
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE' and not subscription:
            return Response(
                {'errors': 'Вы уже удалили этого автора из подписок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        authentication_classes=(TokenAuthentication),
    )
    def followings(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)

        serializer = GetFollowSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)
