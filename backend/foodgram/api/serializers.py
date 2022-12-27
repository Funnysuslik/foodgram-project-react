import base64

from djoser.serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
    User,
)


class Base64ImageField(serializers.ImageField):
    """Pictures decoder with base64 library."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):

            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password', )

class CustomUserSerializer(UserSerializer):
    """"""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, user):
        """"""
        try:
            current_user = self.context.get('user')

            return current_user.subscriber.filter(subscribed=user).exists()

        except AttributeError:

            return False

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')


class TagSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """"""

    # amount = serializers.SerializerMethodField('get_amount')

    # def get_amount(self, ingredient):

    #     return ingredient.ingredient_amount.values_list('amount', flat=True)[0]

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', ) #'amount')


class IngredientWithAmountSerializer(serializers.ModelSerializer):
    """"""

    amount = serializers.SerializerMethodField('get_amount')

    def get_amount(self, ingredient):

        return ingredient.ingredient_amount.values_list('amount', flat=True)[0]

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """"""

    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientWithAmountSerializer(read_only=True, many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    image = Base64ImageField(required=True, allow_null=False)
    # is_in_shopping_cart = serializers.SerializerMethodField(
    #     'get_is_in_shopping_cart'
    # )

    def get_is_favorited(self, recipe):
        # current_user = self.context.get('request').user
        favorite = Favorite.objects.filter(recipe=recipe)
        print(favorite.user)
        return False

    # def get_is_in_shopping_cart(self, recipe):
    #     current_user = self.context.get('request').user
    #     shopping_cart_of_user = current_user.shopping_cart
    #     return

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    # def get_is_favorited(self, obj):

    #     return obj.objects.prefetch_related('favorite').filter(
    #         user=self.context['request'].user,
    #         recipe=obj
    #     ).exists()

    # def get_is_in_shopping_cart(self, obj):

    #     return obj.objects.prefetch_related('shopping_cart').filter(
    #         owner=self.context['request'].user,
    #         recipe=self.obj
    #     ).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = ShoppingCart
        fields = ()


class FavoriteSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Favorite
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Subscription
        fields = '__all__'
