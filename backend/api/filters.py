from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from recipes.models import Recipe
from users.models import User


class IngredientFiltration(SearchFilter):
    search_param = 'name'


class RecipeSearchFilter(filters.FilterSet):

    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='favorites', method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shopping', method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping__user=self.request.user,
            )
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset
