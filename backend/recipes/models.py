from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from foodgram.settings import (INGREDIENT_MAX_LENGTH,
                               RECIPE_NAME_MAX_LENGTH,
                               TAG_MAX_LENGTH, MIN_INGREDIENT_VALUE)

from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=INGREDIENT_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=INGREDIENT_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


filtered_ingredients = Ingredient.objects.filter(
    name__icontains='название инградиента',
)


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=RECIPE_NAME_MAX_LENGTH)
    color = ColorField('Цвет HEX', max_length=TAG_MAX_LENGTH)
    slug = models.SlugField('Cлаг', max_length=RECIPE_NAME_MAX_LENGTH)

    class Meta():
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):

    name = models.CharField(
        'Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex='[А-Яа-яA-Za-z]+[^0-9]',
                message='Название не должно состоять только из цифр и знаков',
            ),
        ],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепты',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredientsMerge',
        related_name='recipes',
    )

    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='media/',
    )

    text = models.TextField(
        verbose_name='Описание',
    )

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                1, message='Время приготовления должно быть больше 1 минуты',
            ),
        ),
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_recipe_author_name',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.author})'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='is_favorited',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} выбран {self.user.username}'


class RecipeIngredientsMerge(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_VALUE,
                message=f'Количество не может быть'
                f'меньше {MIN_INGREDIENT_VALUE}',
            ),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient_merge',
            ),
        ]

    def __str__(self):
        return f'Ингредиент: {self.ingredient}, Рецепт: {self.recipe}'


# class Cart(models.Model):
#     user = models.ForeignKey(
#         User,
#         related_query_name='shopping',
#         verbose_name='Пользователь',
#         on_delete=models.CASCADE,
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         related_query_name='shopping',
#         verbose_name='Рецепт',
#         on_delete=models.CASCADE,
#     )

#     class Meta:
#         verbose_name = 'Рецепт в списке покупок'
#         verbose_name_plural = 'Рецепты в списке покупок'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('user', 'recipe'), name='unique_korzina_user_recipe',
#             ),
#         ]

#     def __str__(self):
#         return f'{self.recipe.name} в списке покупок для {self.user.username}'


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        related_query_name='shopping',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_query_name='shopping',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_cart_user_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке покупок для {self.user.username}'
