from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientsViewSet, RecipesViewSet, TagsViewSet, UsersViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('users', UsersViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
