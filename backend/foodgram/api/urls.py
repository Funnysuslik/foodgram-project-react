from django.urls import path, include
from rest_framework import routers

from .views import (
    DownloadShoppingCart,
    IngredientViewSet,
    FavoriteView,
    RecipeViewSet,
    ShoppingCartView,
    SubscribeView,
    SubscriptionsView,
    TagViewSet,
    CustomUserViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionsView.as_view(),
        name='subscriptions',
    ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe',
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteView.as_view(),
        name='favorite',
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCart.as_view(),
        name='download_shopping_cart'
    ),
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
