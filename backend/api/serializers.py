from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from users.models import User

from .models import (Favorites, Ingredients, IngredientRecipe, Recipes,
                     ShoppingCart, Tags)


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя"""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class SubscribeSerializer(UserSerializer):
    """Сериализатор получения подписок"""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count',
            'recipes',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST)
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиентов и рецепта"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор  рецепта."""
    tags = TagsSerializer(read_only=False, many=True)
    author = CustomUserSerializer(read_only=True, many=False)
    ingredients = IngredientsRecipesSerializer(
        many=True,
        source='ingredientrecipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientsRecipesSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(user=request.user).exists()


class PostRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""
    ingredients = IngredientsRecipesSerializer(
        many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'})
    image = Base64ImageField(max_length=None)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, tags):
        for tag in tags:
            if not Tags.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует')
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления (в минутах). Менее 1 минуты.',
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Ошибки в ингредиентах.')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиент не уникален.')
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента больше 0')
        return ingredients

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_liist = []
        for ingredient_data in ingredients:
            ingredient_liist.append(
                IngredientRecipe(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recipe=recipe))
        IngredientRecipe.objects.bulk_create(ingredient_liist)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request'),
        }).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения краткой информации рецептов."""

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorites
        fields = (
            'user',
            'recipe',
        )

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.',
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request'),
            },
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(
            recipe=data['recipe'],
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request'),
            },
        ).data
