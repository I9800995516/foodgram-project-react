
from django.db import IntegrityError, transaction
from django.db.utils import IntegrityError
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

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
            password = validated_data.pop(
                'password', None)
            user = User.objects.create_user(
                password=password, **validated_data,
            )
            return user


class UniqueUserCreateSerializer(UserSerializer):
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
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            if hasattr(user, 'email'):
                return self.context.get(
                    'request',
                ).user.is_authenticated and Follow.objects.filter(
                    user=user, author=obj,
                ).exists()
        return False

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class GetFollowSerializer(UniqueUserCreateSerializer):
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
                default_detail='Вы уже подписаны на этого автора!',
                default_code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                default_detail="Нелья подписаться на самого себя!",
                default_code=status.HTTP_400_BAD_REQUEST,
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
