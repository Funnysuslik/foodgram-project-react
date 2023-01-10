from django.contrib import admin

from .models import (
    Ingredient,
    IngredientAmount,
    Favorite,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin model for tag model."""

    list_display = ('id', 'name', 'color', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Описание в админки модели ингредиента.
    """

    list_display = ('id', 'name', 'measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Описание в админки модели рецепта.
    """

    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Описание в админки модели списка покупок.
    """

    list_display = ('user', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Описание в админки модели избранного.
    """

    list_display = ('user', 'recipe',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Описание в админки модели подписок.
    """

    list_display = ('user', 'author',)


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    """
    Описание в админки промежуточной модели для ингредиентов.
    """

    list_display = ('recipe', 'ingredient', 'amount',)
