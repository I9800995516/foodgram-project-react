
from django.db import IntegrityError, transaction
from django.db.utils import IntegrityError
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework import status

from .models import Follow, User


class UserCreateMixin:
    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                'Не удалось создать пользователя',
        )
        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
        return user


class CustomUserCreateSerializer(UserSerializer):
    '''Пользовательский сериализатор.'''

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            if hasattr(user, 'email'):
                return Follow.objects.filter(user=user, author=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context.get('request').user.is_authenticated:
            representation['id'] = None
            representation['username'] = ''
            representation['is_subscribed'] = False
            representation.pop('email', None)
        return representation


class GetFollowSerializer(CustomUserCreateSerializer):
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

        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого автора!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail="Нелья подписаться на самого себя!",
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
        return obj.recipes.count()

    class Meta(GetFollowSerializer.Meta):
        fields = GetFollowSerializer.Meta.fields + (
            'recipes_count',
            'recipes',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )
