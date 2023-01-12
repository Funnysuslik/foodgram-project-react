from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Модель тэгов для рецептов (ManyToMany).
    Related names:
    recipe = recipes
    """

    name = models.CharField(
        max_length=200,
    )
    color = models.CharField(
        max_length=7,
    )
    slug = models.SlugField(
        max_length=200,
        validators=[
            RegexValidator('^[-a-zA-Z0-9_]+$'),
        ],
        unique=True,
    )


class Ingredient(models.Model):
    """
    Модель для ингридиентов в рецептах (ManyToMany).
    Related names:
    Recipe = recipes
    IngredientAmount(throught_model) = ingredient_amount
    """

    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )


class Recipe(models.Model):
    """
    Модель рецептов на сайте.
    Related names:
    ingredients(throught_model) = ingredient_amount
    Favorite = favorite
    ShoppingCart = shopping_cart

    """

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientAmount'
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    text = models.TextField()
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999),
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',

    )

    class Meta:
        ordering = ['-pub_date']


class ShoppingCart(models.Model):
    """
    Модель для сохранения ингридентов из рецептов в список покупок.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_shopping_cart'
            )
        ]


class Favorite(models.Model):
    """
    Модель для сохранения рецептов.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_favorite_recipe'
            )
        ]


class Subscription(models.Model):
    """
    Модель для подписки пользователей на авторов рецептов.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe_user',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe_author',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='user_subs_author'
            )
        ]


class IngredientAmount(models.Model):
    """
    Промежуточная модель для ManyToMany связи модели рецептов
    и модели ингредиентов с указанием количество последних.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='ingredient_amount',
    )
    amount = models.IntegerField(
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999),
        ],
    )
