from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.views import APIView, Response
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
)

from . import filters, utils
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeForSubSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer,
    CustomUserSerializer,
)
from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
    User,
)


class CustomUserViewSet(UserViewSet):
    """
    Кастомный UserViewSet для корректной работы djoser.
    Пермишены настроены в самом djoser.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class TagViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet для модели тэгов
    Permission доступен для всех, оба метода безопасны,
    в документации особых укзаний не было.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny,]
    pagination_class = None


class IngredientViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet для модели ингредиентов
    Permission доступен для всех, оба метода безопасны,
    в документации особых укзаний не было.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = filters.IngredientFilter
    permission_classes = [AllowAny,]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Стандартный ModelViewSet для модели рецептов.
    Применён кастомный фильтр, правильность работы под (?).
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = filters.RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):

            return RecipeSerializer

        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ShoppingCartView(APIView):
    """
    Вью класс для добавления и удаления рецептов в список покупок.
    """

    permission_classes = [IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(pk=kwargs.get('recipe_id', None))

        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():

            return Response(
                {'error': 'You can\'t add this recipe to shopping cart again'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ShoppingCart.objects.create(user=request.user, recipe=recipe)

        serializer = RecipeForSubSerializer(
            recipe,
            context={'request': request, 'recipe': recipe},
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(pk=kwargs.get('recipe_id', None))

        try:
            ShoppingCart.objects.get(recipe=recipe, user=request.user).delete()
        except Favorite.DoesNotExist:

            return Response(
                {'error': 'This recipe is not in your shopping cart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @classmethod
    def get_extra_actions(cls):
        return []


class FavoriteView(APIView):
    """
    Вью для добавления и удаления рецепта в избраное.
    """

    permission_classes = [IsAuthenticated,]
    pagination_class = None

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('recipe_id', None)
        recipe = get_object_or_404(Recipe, pk=pk)
        if Favorite.objects.filter(
            user=request.user, recipe=recipe
        ):

            return Response(
                {'error': 'You can\'t add this recipe to favorites again'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Favorite.objects.create(user=request.user, recipe=recipe)

        serializer = RecipeForSubSerializer(
            recipe, context={'request': request, 'recipe': recipe}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('recipe_id', None)
        recipe = get_object_or_404(Recipe, pk=pk)

        try:
            Favorite.objects.get(recipe=recipe, user=request.user).delete()
        except Favorite.DoesNotExist:

            return Response(
                {'error': 'You are not add this recipe in favorite before'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @classmethod
    def get_extra_actions(cls):
        return []


class SubscriptionsView(APIView, LimitOffsetPagination):
    """
    Вью класс для просмотра подписок.
    """

    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        authors = User.objects.filter(subscribe_author__user=request.user)

        result_pages = self.paginate_queryset(authors, request, view=self)

        serializer = SubscribeSerializer(
            result_pages, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @classmethod
    def get_extra_actions(cls):
        return []


class SubscribeView(APIView):
    """
    Вью класс для подписки и отписки на авторов рецептов.
    """

    permission_classes = [IsAuthenticated,]
    pagination_class = None

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('user_id', None)
        author = get_object_or_404(User, pk=pk)
        if author == request.user or Subscription.objects.filter(
            user=request.user, author=author
        ):

            return Response(
                {
                    'error': 'You can\'t subscribe on this user',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=request.user, author=author)

        serializer = SubscribeSerializer(
            author, context={'request': request, 'author': author}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('user_id', None)
        author = get_object_or_404(User, pk=pk)

        try:
            Subscription.objects.get(author=author, user=request.user).delete()
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'You don\'t subscribed on this user'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @classmethod
    def get_extra_actions(cls):
        return []


class DownloadShoppingCart(APIView):
    """
    Вью класс для скачивания списка покупок.
    """

    permission_classes = [AllowAny,]
    pagination_class = None

    def get(self, *args, **kwargs):
        """"""
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        data = ShoppingCartSerializer(
            shopping_cart,
            many=True,
            context={'request': self.request}
        ).data
        filename = 'shoppingcart.pdf'
        http_status = status.HTTP_200_OK

        return utils.make_pdf(
            data=data,
            filename=filename,
            http_status=http_status
        )
