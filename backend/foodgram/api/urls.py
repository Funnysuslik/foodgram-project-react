from django.urls import path, include
from rest_framework import routers

from .views import (
    DownloadShoppingCart,
    IngredientViewSet,
    FavoriteViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    SubscribeViewSet,
    SubscriptionsViewSet,
    TagViewSet,
    CustomUserViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'users/subscriptions', SubscriptionsViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'recipes/(?P<recipe_id>\d+)/sopping_cart',
                ShoppingCartViewSet)
router.register(r'download_shopping_cart', DownloadShoppingCart)
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
