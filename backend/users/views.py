from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from api.pagination import CustomPagination

from .models import Follow, User
from .serializers import (AddFollowerSerializer, GetFollowSerializer,
                          FieldUserSerializer)


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = FieldUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        authentication_classes=[TokenAuthentication],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        subscription = Follow.objects.filter(
            follower=user,
            author=author,
        )

        if request.method == 'POST':
            serializer = AddFollowerSerializer(
                data=request.data,  # Pass request data instead of `author`
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(follower=user, author=author)
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
        authentication_classes=[TokenAuthentication],
    )
    def suscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        queryset = user.following.all()
        pages = self.paginate_queryset(queryset)

        serializer = GetFollowSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)
