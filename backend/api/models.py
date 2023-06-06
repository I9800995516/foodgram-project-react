from colorfield.fields import ColorField
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User

LENGTH = 200


class Ingredients(models.Model):
    """Ингредиенты."""
    name = models.CharField(
        max_length=LENGTH,
        verbose_name='Название ингредиента',
        db_index=True)
    measurement_unit = models.CharField(
        max_length=LENGTH,
        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit')]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tags(models.Model):
    """Теги."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=LENGTH,
        db_index=True,
        unique=True)
    color = ColorField(
        verbose_name='HEX-код',
        format='hex',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message='Проверьте вводимый формат')],
    )
    slug = models.SlugField(
        max_length=LENGTH,
        verbose_name='Slug',
        unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Рецепты."""
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes')
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH)
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        through='IngredientRecipe')
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(
                1, message='Время приготовления не менее 1 минуты!'),
            MaxValueValidator(
                1441, message='Время приготовления не более 24 часов!'),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class FavoriteShoppingCart(models.Model):
    """Список покупок и избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепты')

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'),
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorites(FavoriteShoppingCart):
    """Добавление в избраное."""

    class Meta(FavoriteShoppingCart.Meta):
        related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(FavoriteShoppingCart):
    """Список покупок."""

    class Meta(FavoriteShoppingCart.Meta):
        related_name = 'shopping_list'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class IngredientRecipe(models.Model):
    """Ингредиенты рецепта."""
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredientrecipe')
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество ингредиента')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'),
        ]

    def __str__(self):
        return (f'{self.ingredient.name} :: '
                f'{self.ingredient.measurement_unit}'
                f' - {self.amount} ')
