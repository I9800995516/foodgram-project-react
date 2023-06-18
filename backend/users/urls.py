from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'users'

router = DefaultRouter()

router.register('users', UsersViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, 'recipes')


urlpatterns = [

    path('', include(router.urls)),

]
