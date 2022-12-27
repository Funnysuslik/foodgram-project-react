from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, renderers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
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
from .serializers import (
    IngredientSerializer,
    FavoriteSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer,
    CustomUserSerializer,
)


class OneResultSetPagination(PageNumberPagination):
    """"""

    page_size = 1
    page_size_query_param = 'page_size'


class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class CustomUserViewSet(UserViewSet):
    """"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = OneResultSetPagination


class TagViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    """"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny,]


class IngredientViewSet(ListModelMixin,
                        RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'name'
    permission_classes = [AllowAny,]


class RecipeViewSet(CreateModelMixin,
                    DestroyModelMixin,
                    ListModelMixin,
                    RetrieveModelMixin,
                    UpdateModelMixin,
                    viewsets.GenericViewSet):
    """"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = OneResultSetPagination
    permission_classes = [AllowAny,]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ShoppingCartViewSet(CreateModelMixin,
                          DestroyModelMixin,
                          viewsets.GenericViewSet):
    """"""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [AllowAny,]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DownloadShoppingCart(RetrieveModelMixin, viewsets.GenericViewSet):
    """"""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [AllowAny,]

    def get_queryset(self):
        owner = self.request.user

        return ShoppingCart.objects.filter(owner=owner)

    # @action(
    #   methods=['get'],
    #   detail=True,
    #   renderer_classes=(PassthroughRenderer,)
    # )
    # def download(self, *args, **kwargs):
    #     """"""

    #     instance = self.get_object()

    #     file_handle = instance.file.open()

    #     response = FileResponse(file_handle, content_type='whatever')
    #     response['Content-Length'] = instance.file.size
    #     response['Content-Disposition'] = 'attachment; filename="%s"' % instance.file.name

    #     return response


class FavoriteViewSet(CreateModelMixin,
                      DestroyModelMixin,
                      viewsets.GenericViewSet):
    """"""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny,]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                pk=self.kwargs.get['recipe_id']
            )
        )


class SubscriptionsViewSet(ListModelMixin,
                           viewsets.GenericViewSet):
    """"""

    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer
    pagination_class = OneResultSetPagination
    permission_classes = [AllowAny,]

    def get_queryset(self):
        subscriber = self.request.user

        return Subscription.objects.filter(subscriber=subscriber)


class SubscribeViewSet(CreateModelMixin,
                       DestroyModelMixin,
                       viewsets.GenericViewSet):
    """"""

    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = [AllowAny,]

    def perform_create(self, serializer):
        serializer.save(
            subscriber=self.request.user,
            subscribeing=self.kwargs.get['user_id']
        )
