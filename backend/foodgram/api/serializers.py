from djoser.serializers import UserSerializer, UserCreateSerializer
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    IngredientAmount,
    Favorite,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
    User,
)


class CustomUserSerializer(UserSerializer):
    """
    Кастомный сериализатор для корректной работы djoser
    при авторизации с парой пароль + имейл.
    """

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, user):

        try:
            current_user = self.context.get('user')

            return current_user.subscriber.filter(subscribed=user).exists()

        except AttributeError:

            return False

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', )  # 'recipes', )
        read_only_fields = ('email',)


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Кастомный сериализатор для создания пользователя с djoser.
    """

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериалзизатор для модели ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientWithAmountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов с данными из промежуточной
    модели о количестве ингредента в рецепте.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeCreateIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиента для создания рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeCreateTagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тэга для создания рецепта.
    """

    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецепта.
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = RecipeCreateIngredientSerializer(
        source='ingredient_amount',
        many=True,
    )
    author = UserSerializer(required=False)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_amount')
        tags = validated_data.pop('tags')

        obj = Recipe.objects.create(**validated_data)
        obj.save()

        obj.tags.set(tags)

        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=obj,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            ).save()

        return obj

    @transaction.atomic
    def update(self, instanse, validated_data):
        ingredients = validated_data.pop('ingredient_amount')
        tags = validated_data.pop('tags')

        for field, value in validated_data.items():
            setattr(instanse, field, value)

        instanse.tags.set(tags),
        instanse.image = validated_data.get('image', instanse.image)

        instanse.ingredients.clear()
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=instanse,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            ).save()

        return super().update(instanse, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов. Обычный.
    """

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer(required=False)
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_in_shopping_cart(self, obj):

        try:

            return ShoppingCart.objects.filter(
                recipe=obj, user=self.context['request'].user
            ).exists()

        except TypeError:

            return False

    def get_is_favorited(self, obj):
        try:

            return Favorite.objects.filter(
                recipe=obj, user=self.context['request'].user
            ).exists()

        except TypeError:

            return False

    def get_ingredients(self, obj):

        return IngredientWithAmountSerializer(
            IngredientAmount.objects.filter(recipe=obj).all(),
            many=True
        ).data

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


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка покупок.
    """

    class Meta:
        model = ShoppingCart
        fields = '__all__'


class RecipeForSubSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецепта. Короткий.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписок на пользователей.
    """

    email = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_email(self, obj):

        return obj.email

    def get_id(self, obj):

        return obj.id

    def get_username(self, obj):

        return obj.username

    def get_first_name(self, obj):

        return obj.first_name

    def get_last_name(self, obj):

        return obj.last_name

    def get_is_subscribed(self, obj):

        return True

    def get_recipes(self, obj):
        recipes = obj.recipes

        return RecipeForSubSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):

        return obj.recipes.count()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра подписок.
    """

    email = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_email(self, obj):

        return obj.email

    def get_id(self, obj):

        return obj.pk

    def get_username(self, obj):

        return obj.username

    def get_first_name(self, obj):

        return obj.first_name

    def get_last_name(self, obj):

        return obj.last_name

    def get_is_subscribed(self, obj):

        return True

    def get_recipes(self, obj):
        recipes = obj.recipes

        return RecipeForSubSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):

        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
