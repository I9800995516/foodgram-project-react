import base64
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsMerge, RecipeKorzina, Tag)
from rest_framework import serializers
from rest_framework.fields import ImageField
from rest_framework.serializers import (CurrentUserDefault, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator
from users.models import User
from users.serializers import FieldUserSerializer


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.BooleanField(default=False)

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed',)


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializers(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]


class IngredientNoAmountSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='id',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredientsMerge
        fields = ('ingredient', 'name', 'measurement_unit', 'amount')


class RecipeIngredientsMergeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientsMerge
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializers(many=True, read_only=True)
    author = FieldUserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )

    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(max_length=None)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if (
            request.user.is_authenticated
            and Favorite.objects.filter(
                recipe=obj,
                user=request.user,
            ).exists()
        ):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if (
            request.user.is_authenticated
            and RecipeKorzina.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        ):
            return True
        return False

    class Meta:
        model = Recipe
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
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name'],
            ),
        ]


class FavoriteSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(
        read_only=True, default=CurrentUserDefault(),
    )
    recipe = PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        recipe = validated_data.get('recipe')

        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError('Этот рецепт уже был добавлен в избранное!')

        return Favorite.objects.create(user=user, recipe=recipe)

    def validate(self, data):
        recipe = data['recipe']
        user = self.context['request'].user

        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError('Этот рецепт уже был добавлен в избранное!')

        return data

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')


class RecipeKorzinaSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(
        read_only=True, default=CurrentUserDefault(),
    )
    recipe = PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    def create(self, validated_data):
        return RecipeKorzina.objects.create(
            user=self.context.get('request').user,
            **validated_data,
        )

    def validate(self, data):
        object = RecipeKorzina.objects.filter(
            recipe=data['recipe'],
            user=self.context['request'].user,
        )
        if self.context['request'].method == 'DELETE':
            raise ValidationError(
                'Этот рецепт не был добавлен в список покупок!',
            )
        if self.context['request'].method == 'POST' and object.exists():
            raise ValidationError(
                'Этот рецепт уже был добавлен в список покупок!',
            )

        return data

    class Meta:
        model = RecipeKorzina
        fields = ('recipe', 'user')


class RecipeIngredientSerializer(serializers.Serializer):
    """Сериализатор для добавления ингредиентов в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='Количество не может быть менее 1',
            ),
            MaxValueValidator(
                1000,
                message='Мы столько не сьедим....',
            ),
        ),
    )

    def validate_id(self, obj):
        if not Ingredient.objects.filter(id=obj).exists():
            raise ValidationError('Такого ингредиента нет.')

        return obj


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = FieldUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        print(f'Ингредиенты: {ingredients}')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        self.save_ingredients(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time,
        )

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance.tags.set(tags)
        instance.ingredients.clear()

        self.save_ingredients(instance, ingredients)

        instance.save()
        return instance

    @staticmethod
    def save_ingredients(recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = ingredient.get('id')
            current_amount = ingredient.get('amount')
            ingredients_list.append(
                RecipeIngredientsMerge(
                    recipe=recipe,
                    ingredient_id=current_ingredient,
                    amount=current_amount,
                ),
            )
        RecipeIngredientsMerge.objects.bulk_create(ingredients_list)

    def validate(self, data):
        cooking_time = data.get('cooking_time')
        if not isinstance(cooking_time, int):
            raise serializers.ValidationError(
                {'error': 'Время приготовления должно быть целым числом!'},
            )
        if cooking_time <= 0:
            raise serializers.ValidationError(
                {'error': 'Время приготовления должно быть не менее 1 мин!'},
            )

        return data

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')},
        )
        return serializer.data
    
    
    class Meta:
        model = Recipe
        fields = '__all__'
