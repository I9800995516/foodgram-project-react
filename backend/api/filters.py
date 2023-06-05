from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter
from distutils.util import strtobool

from .models import Ingredients, Recipes, Tags, ShoppingCart, Favorites


class IngredientsFilter(SearchFilter):
    search_param = 'name'
    name = filters.CharFilter(
        lookup_expr='startswith',
    )

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipesFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='is_favorited_method')
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_method')

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipes.objects.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        favorites = Favorites.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in favorites]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipes.objects.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
