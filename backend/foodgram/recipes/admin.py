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
        'favorite_count',
        'shoppingcart_count',
    )
    search_fields = (
        'name',
        'author__username',
        'author__first_name',
        'author__last_name',
        'tags__name',
        'tags__slug',
    )
    readonly_fields = ('favorite_count', 'shoppingcart_count')

    def favorite_count(self, obj):

        return obj.favorite.count()

    def shoppingcart_count(self, obj):

        return obj.shopping_cart.count()


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
