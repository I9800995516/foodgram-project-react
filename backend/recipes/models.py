from colorfield.fields import ColorField
from django.core.validators import RegexValidator
from django.db import models
from foodgram.settings import (INGREDIENT_MAX_LENGTH, RECIPE_NAME_MAX_LENGTH,
                               TAG_MAX_LENGTH)
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=INGREDIENT_MAX_LENGTH,
        unique=True,
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=INGREDIENT_MAX_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


filtered_ingredients = Ingredient.objects.filter(
    name__icontains='название инградиента',
)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=RECIPE_NAME_MAX_LENGTH,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет HEX',
        max_length=TAG_MAX_LENGTH,
        unique=True,
    )

    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=RECIPE_NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta():
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепты',
    )

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex='[А-Яа-яA-Za-z]+[^0-9]',
                message='Название не должно состоять только из цифр и знаков',
            ),
        ],
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientsMerge',
        related_name='recipes',
        verbose_name='Ингредиенты',
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
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )

    class Meta():
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='уникальное имя пользователя',
            ),
        ]

    def __str__(self):
        return self.name


class RecipeIngredientsMerge(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredamount',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredamount',
    )

    amount = models.CharField('Количество', max_length=RECIPE_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='уникальный ингредиент рецепта',
            ),
        ]

    def __str__(self):
        return f'Ингредиент: {self.ingredient}, Рецепт: {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='избранный',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} выбран {self.user.username}'


class RecipeKorzina(models.Model):
    user = models.ForeignKey(
        User,
        related_name='korzina',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='korzina',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_korzina',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке покупок для {self.user.username}'
