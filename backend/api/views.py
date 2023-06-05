from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Follower, User

from .filters import IngredientsFilter, RecipesFilter
from .models import (Favorites, Ingredients, IngredientRecipe, Recipes,
                     ShoppingCart, Tags)
from .pagination import Pagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (PostRecipeSerializer, FavoriteSerializer,
                          IngredientsSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagsSerializer, UserSerializer)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод ингредиентов."""
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientsFilter,)
    search_fields = ('name',)
    pagination_class = None


class TagsViewSet(viewsets.ModelViewSet):
    """Вывод тегов."""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вывод рецептов."""
    queryset = Recipes.objects.all()
    serializer_class = PostRecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return PostRecipeSerializer

    @staticmethod
    def send_message(ingredients):
        """Отправить список покупок."""
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        """Загрузить список покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user,
        ).order_by('ingredient__name').values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(detail=True, methods=('POST',),
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Добавить рецепт в корзину покупок пользователя."""
        context = {'request': request}
        recipe = get_object_or_404(Recipes, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id,
        }
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        """Удалить рецепт из корзины."""
        get_object_or_404(
            ShoppingCart, user=request.user.id,
            recipe=get_object_or_404(Recipes, id=pk),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST',),
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Добавить рецепт в избранное и в корзину."""
        context = {"request": request}
        recipe = get_object_or_404(Recipes, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id,
        }
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        """Удалить рецепт из избранного у текущего пользователя."""
        get_object_or_404(
            Favorites,
            user=request.user,
            recipe=get_object_or_404(Recipes, id=pk),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Подписаться на автора /отписаться от автора."""
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            Follower.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Follower, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список подписок пользователя."""
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
