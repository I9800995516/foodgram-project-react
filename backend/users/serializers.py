
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from .models import Follow, User
from recipes.models import Recipe


class FieldUserSerializer(UserSerializer):
    """Сериализатор пользователя с дополнительным полем."""
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

        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(follower=user, author=obj).exists()


class GetFollowSerializer(FieldUserSerializer):
    """Сериализатора подписчика."""
    recipes = SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True,
    )
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes_count',
            'recipes',
            'is_subscribed',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeFollowSerializer(
            recipes, many=True, context=self.context,
        )
        return serializer.data


class RecipeFollowSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AddFollowerSerializer(GetFollowSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if author is not None:
            if Follow.objects.filter(author=author, follower=user).exists():
                raise ValidationError(
                    detail=f'Вы уже подписаны на этого {author}!',
                    code=status.HTTP_400_BAD_REQUEST,
                )
            if user == author:
                raise ValidationError(
                    detail='Нельзя подписаться на самого себя!',
                    code=status.HTTP_400_BAD_REQUEST,
                )

        return data

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeFollowSerializer(
            recipes, many=True, context=self.context,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta(GetFollowSerializer.Meta):
        fields = GetFollowSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )
