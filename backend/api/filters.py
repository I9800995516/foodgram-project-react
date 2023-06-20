from django_filters import rest_framework as filters
from recipes.models import Recipe
<<<<<<< HEAD
from rest_framework.filters import SearchFilter
=======
>>>>>>> master

from users.models import User


<<<<<<< HEAD
class IngredientFiltration(SearchFilter):

    search_param = 'name'


=======
>>>>>>> master
class RecipeSearchFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_korzina',
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_is_in_korzina(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(korzina__user=user)
        return queryset
