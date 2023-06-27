from django.db.models import Sum
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from api.recipepdf import recipe_pdf_download
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsMerge, RecipeKorzina, Tag)

from .filters import IngredientFiltration, RecipeSearchFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (IsRecipeAuthorOrReadOnly,
                          IsSuperUserIsAdminIsModeratorIsAuthor)
from .serializers import (FavoriteSerializer, IngredientNoAmountSerializer,
                          RecipeCreateSerializer, RecipeKorzinaSerializer,
                          RecipeSerializer, TagSerializers)


class TagViewSet(CreateListDestroyViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializers
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientNoAmountSerializer
    pagination_class = None
    http_method_names = ['get']
    filter_backends = (IngredientFiltration,)
    search_fields = ('^name',)
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = (IsRecipeAuthorOrReadOnly,)
    permission_classes = [AllowAny]
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

    def add_del(self, request, pk, model, serializer):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            if model.objects.filter(recipe=recipe, user=request.user).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(
                recipe=recipe, user=request.user, author=request.user,
            )
        elif request.method == 'DELETE':
            action_model = get_object_or_404(
                model,
                user=request.user,
                recipe=get_object_or_404(Recipe, pk=pk),
            )
            action_model.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = serializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        return self.add_del(request, pk, Favorite, FavoriteSerializer)

    @action(methods=['post', 'delete'], detail=True)
    def korzina(self, request, pk):
        return self.add_del(
            request, pk, RecipeKorzina, RecipeKorzinaSerializer,
        )

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_korzina(self, request):
        user = request.user
        ingredients = (
            RecipeIngredientsMerge.objects.filter(
                recipe__recipekorzina__user=user,
            )
            .prefetch_related('recipe___recipekorzina', 'user', 'ingredient')
            .values_list('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )

        output = ['Список ваших покупок:\n']
        for i, (name, unit, amount) in enumerate(ingredients, start=1):
            output.append(f'{i}. {name} - {amount} {unit}\n')

        file_name = 'korzina.txt'
        response = HttpResponse(content_type='text/plain')
        response['Список покупок'] = f'attachment; filename={file_name}'
        response.write(''.join(output))

        return response

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_recipe_korzina(self, request):
        user = request.user
        ingredients = RecipeIngredientsMerge.objects.filter(
            recipe__recipekorzina__user=user,
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount=Sum('amount'))

        data = []
        for ingredient in ingredients:
            data.append(
                f'• {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["amount"]}',
            )

        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'korzina.txt'

        response = HttpResponse(content, content_type='text/plain')
        response['Список покупок'] = f'attachment; filename={filename}'

        return response

    @action(detail=False, methods=['get'],
            permission_classes=[IsSuperUserIsAdminIsModeratorIsAuthor])
    def recipe_pdf_download(self, request):
        return recipe_pdf_download(request)

    @action(detail=True, methods=['get'])
    def custom_retrieve(self, request, pk=None):
        return self.retrieve(request)
