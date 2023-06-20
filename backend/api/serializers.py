from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
<<<<<<< HEAD
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsMerge, RecipeKorzina, Tag)
=======
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredientsMerge, RecipeKorzina, Tag,
)
>>>>>>> master
from rest_framework.serializers import (CharField, CurrentUserDefault,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField)
from rest_framework.validators import UniqueTogetherValidator
<<<<<<< HEAD
from users.serializers import UniqueUserCreateSerializer
=======
from users.serializers import CustomUserCreateSerializer
>>>>>>> master


class TagSerializers(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializers(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredientsMerge
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
<<<<<<< HEAD
    author = UniqueUserCreateSerializer()
=======
    author = CustomUserCreateSerializer()
>>>>>>> master
    tags = TagSerializers(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipeingredients',
        many=True,
        read_only=True,
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

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
            'author',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time',
            'pub_date',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name'],
            ),
        ]


class RecipeCreateSerializer(ModelSerializer):
<<<<<<< HEAD
    author = UniqueUserCreateSerializer(
=======
    author = CustomUserCreateSerializer(
>>>>>>> master
        read_only=True,
        default=CurrentUserDefault(),
    )
    ingredients = IngredientInRecipeSerializer(
        source='RecipeIngredients',
        many=True,
    )
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(
        required=False,
        allow_null=True,
    )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('RecipeIngredientsMerge')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.add(*tags)
        self.save_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        ingredients = validated_data.pop('RecipeIngredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        instance.ingredients.clear()
        recipe = instance
        self.save_ingredients(recipe, ingredients)
        instance.save()
        return instance

    @staticmethod
    def save_ingredients(recipe, ingredients):
        ingredietnts_in_recipe = []
        for ingredient in ingredients:
            current_ingredient = ingredient['ingredient']['id']
            current_amount = ingredient.get('amount')
            ingredietnts_in_recipe.append(
                RecipeIngredientsMerge(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=current_amount,
                ),
            )
        RecipeIngredientsMerge.objects.bulk_create(ingredietnts_in_recipe)

    def validate(self, data):
        ingredietnts_in_recipe = []
        ingredients_in_recipe = data.get('RecipeIngredients')
        for ingredient in ingredients_in_recipe:
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    {
                        'error': 'Ингредиентов не должно быть менее одного!',
                    },
                )
            ingredietnts_in_recipe.append(ingredient['ingredient']['id'])
        if len(ingredietnts_in_recipe) > len(set(ingredietnts_in_recipe)):
            raise ValidationError(
                {
                    'error': 'Ингредиенты в рецепте не должны повторяться!',
                },
            )
        cooking_time = data.get('cooking_time')
        if cooking_time <= 0:
            raise ValidationError(
                {
                    'error': 'Время приготовления должно быть не менее 1 мин!',
                },
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
        fields = (
            'author',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time',
            'pub_date',
            'tags',
            'is_favorited'
            'is_in_shopping_cart',
        )


class FavoriteSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(
        read_only=True, default=CurrentUserDefault())
    recipe = PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    def create(self, validated_data):
        return Favorite.objects.create(
            user=self.context.get('request').user, **validated_data)

    def validate(self, data):
        object = Favorite.objects.filter(
            recipe=data['recipe'],
            user=self.context['request'].user,
        )
        if self.context['request'].method == 'DELETE':
            raise ValidationError(
                'Этот рецепт не был добавлен в избранное!',
            )
        if self.context['request'].method == 'POST' and object.exists():
            raise ValidationError(
                'Этот рецепт уже был добавлен в избранное!',
            )

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
