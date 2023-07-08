from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.recipepdf import recipe_pdf_download
from recipes.models import Favorite, Ingredient, Recipe, Cart, Tag
from .filters import IngredientFiltration, RecipeSearchFilter
from .mixins import CreateListDestroyViewSet
from .permissions import IsRecipeAuthorOrReadOnly
from .serializers import (
    IngredientNoAmountSerializer,
    ListRecipeSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializers,
)


class TagViewSet(CreateListDestroyViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializers
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientNoAmountSerializer
    permission_classes = (IsRecipeAuthorOrReadOnly,)
    pagination_class = None
    http_method_names = ['get']
    filter_backends = (IngredientFiltration,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsRecipeAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter
    http_method_names = ('get', 'post', 'delete', 'patch')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    @transaction.atomic
    def _add_delete_recipe_to_list(request, recipe_id, list):
        select_list = {
            'favorite': {
                'model': Favorite,
                'name': 'favorite',
            },
            'shopping_cart': {
                'model': Cart,
                'name': 'shopping cart',
            },
        }

        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = request.user

        if request.method == 'POST':
            if select_list[list]['model'].objects.filter(
                    user=user, recipe=recipe,
            ).exists():
                return Response(
                    {'errors': (
                        f'Recipe already added to {select_list[list]["name"]}.'
                    )},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            select_list[list]['model'].objects.create(recipe=recipe, user=user)
            serializer = ListRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not select_list[list]['model'].objects.filter(
                    user=user, recipe=recipe,
            ).exists():
                return Response(
                    {'errors': (
                        f'Рецепт не в списке {select_list[list]["name"]}.'
                    )},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            select_list[list]['model'].objects.filter(
                user=user, recipe=recipe,
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['post', 'delete'],
        url_path='(?P<recipe_id>[^/.]+)/favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, recipe_id=None):
        return self._add_delete_recipe_to_list(request, recipe_id, 'favorite')

    @action(
        detail=False, methods=['post', 'delete'],
        url_path='(?P<recipe_id>[^/.]+)/shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, recipe_id=None):
        return self._add_delete_recipe_to_list(
            request, recipe_id, 'shopping_cart',
        )

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        return recipe_pdf_download(request)
