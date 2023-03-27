from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (AddDeleteFavoriteRecipe, AddDeleteShoppingCart,
                    FollowViewSet, IngredientsViewSet, RecipeViewSet,
                    TagViewSet, UserViewSet)

router = DefaultRouter()

router.register("users", UserViewSet, basename="user")
router.register("follow", FollowViewSet, basename="follow")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("tag", TagViewSet, basename="tag")

urlpatterns = [
    path(
        "recipes/<int:recipe_id>/favorite/",
        AddDeleteFavoriteRecipe.as_view(),
        name="favorite_recipe",
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        "recipes/<int:recipe_id>/shopping_cart/",
        AddDeleteShoppingCart.as_view(),
        name="shopping_cart",
    ),
    path("", include(router.urls)),
]
