import base64

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction

from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.fields import ImageField
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator

from foodgram.settings import MAX_INGREDIENT_VALUE, MIN_INGREDIENT_VALUE
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredientsMerge,
    Tag,
)
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
        fields = ('id', 'ingredient_id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializers(many=True, read_only=True)
    author = FieldUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(max_length=None)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if Favorite.objects.filter(recipe=obj, user=request.user).exists():
                return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if (
            request.user.is_authenticated
            and Cart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        ):
            return True
        return False

    def get_ingredients(self, obj):
        return RecipeIngredientsMergeSerializer(
            obj.recipe_ingredients.all(),
            many=True,
            context=self.context,
        ).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['ingredients'] = [
            {
                'id': ingredient['ingredient_id'],
                'name': ingredient['name'],
                'measurement_unit': ingredient['measurement_unit'],
                'amount': ingredient['amount'],
            }
            for ingredient in data['ingredients']
        ]
        return data

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


class ListRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_VALUE,
                message=(
                    f'Кол-во ингредиентов не может быть меньше '
                    f'{MIN_INGREDIENT_VALUE}.'
                ),
            ),
            MaxValueValidator(
                MAX_INGREDIENT_VALUE,
                message=(
                    f'Нам столько не сьесть,'
                    f'количество должно быть меньше {MAX_INGREDIENT_VALUE}.'
                ),
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
            current_ingredient_id = ingredient.get('id')
            current_amount = int(ingredient.get('amount'))
            if current_ingredient_id is None:
                raise serializers.ValidationError(
                    'Некорректный ID ингредиента',
                )
            try:
                ingredient_obj = Ingredient.objects.get(
                    id=current_ingredient_id,
                )
                ingredients_list.append(
                    RecipeIngredientsMerge(
                        recipe=recipe,
                        ingredient=ingredient_obj,
                        amount=current_amount,
                    ),
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    'Ингредиент с ID {} не существует'
                    .format(current_ingredient_id),
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
