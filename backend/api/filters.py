from django_filters import rest_framework as filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter
from users.models import User
from django_filters import rest_framework


class IngredientFiltration(SearchFilter):

    search_param = 'name'


# class RecipeSearchFilter(filters.FilterSet):
#     author = filters.ModelChoiceFilter(
#         queryset=User.objects.all(),
#     )
#     is_favorited = filters.BooleanFilter(
#         method='filter_is_favorited',
#     )
#     is_in_shopping_cart = filters.BooleanFilter(
#         method='filter_is_in_korzina',
#     )
#     tags = filters.AllValuesMultipleFilter(
#         field_name='tags__slug',
#     )

#     class Meta:
#         model = Recipe
#         fields = (
#             'author',
#             'tags',
#             'is_favorited',
#             'is_in_shopping_cart',
#         )

#     def filter_is_favorited(self, queryset, name, value):
#         user = self.request.user
#         if value and not user.is_anonymous:
#             return queryset.filter(favorite__user=user)
#         return queryset

#     def filter_is_in_korzina(self, queryset, name, value):
#         user = self.request.user
#         if value and user.is_authenticated:
#             return queryset.filter(recipekorzina__user=user)
#         return queryset


class RecipeSearchFilter(rest_framework.FilterSet):
    author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
    tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = rest_framework.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping__user=self.request.user)
        return queryset
