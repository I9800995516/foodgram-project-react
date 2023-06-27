from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UsersViewSet

app_name = 'users'

router = DefaultRouter()

router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('api/', include(router.urls)),
    # re_path(
    #     r'^api/recipes/(?P<pk>\d+)/$', RecipeViewSet.as_view({'get': 'retrieve'}), name='recipe-detail',
    # ),
]
