
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from foodgram.settings import EMPTY

from .models import Favorite, Ingredient, Recipe, RecipeKorzina, Tag


class RecipeIngredList(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty = EMPTY


class AuthorFilter(SimpleListFilter):
    title = _('Author')
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        return Recipe.objects.order_by('author').values_list(
            'author', 'author__username',
        ).distinct()

    def queryset(self, request, queryset):
        author_id = self.value()
        if author_id:
            return queryset.filter(author_id=author_id)
        return queryset


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'pub_date')
    list_filter = (AuthorFilter, 'name', 'tags')
    search_fields = ('name',)
    related_fields = ('author', 'name', 'tags', 'pub_date')
    inlines = (RecipeIngredList,)
    empty = EMPTY

    def is_in_favorited(self, instance):
        return instance.favorites.count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    list_select_related = ('recipe', 'ingredient')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'recipe']
    search_fields = ['user', 'recipe']
    list_select_related = ['user', 'recipe']


class RecipeKorzinaAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeKorzina, RecipeKorzinaAdmin)
