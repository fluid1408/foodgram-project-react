from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    FollowViewSet,
    IngredientsViewSet,
    RecipeViewSet,
    TagViewSet,
    download_shopping_cart,
    AddDeleteFavoriteRecipe,
    AddDeleteShoppingCart
)

router = DefaultRouter()

router.register('users', UserViewSet, basename='user')
router.register('follow', FollowViewSet, basename='follow')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('tag', TagViewSet, basename='tag')

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        AddDeleteFavoriteRecipe.as_view(),
        name='favorite_recipe'),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        AddDeleteShoppingCart.as_view(),
        name='shopping_cart'),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(router.urls)),
]