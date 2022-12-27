from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """"""

    name = models.CharField(
        max_length=200,
    )
    color = models.CharField(
        max_length=7,
    )
    slug = models.CharField(
        max_length=200,
        validators=[
            RegexValidator('^[-a-zA-Z0-9_]+$'),
        ],
        unique=True,
    )


class Ingredient(models.Model):
    """"""

    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        null=False,
    )


class Recipe(models.Model):
    """"""

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=False,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        blank=False,
    )
    name = models.CharField(
        null=False,
        blank=False,
        max_length=200,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        null=False,
    )
    text = models.TextField(
        null=False,
        blank=False,
    )
    cooking_time = models.IntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999),
        ]
    )


class ShoppingCart(models.Model):
    """"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        blank=False,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        blank=False,
    )


class Favorite(models.Model):
    """"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        blank=False,
    )


class Subscription(models.Model):
    """"""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    subscribed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
    )


class IngredientAmount(models.Model):
    """"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
    )
    amount = models.IntegerField(
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999),
        ],
    )
