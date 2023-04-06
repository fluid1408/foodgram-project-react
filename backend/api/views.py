from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PaginationClass
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             RecipeSerializer, ShortRecipeSerializer,
                             SubscriptionsSerializer, TagSerializer,
                             UserSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipe.models import (FavoriteRecipe, IngredientRecipe, Ingredients,
                           Recipe, ShoppingCart, Tag)
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)
from users.models import Follow, User


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, IngredientFilter)
    search_fields = ('^name',)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PaginationClass


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PaginationClass
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)


class FavoriteViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteRecipe.objects.filter(user=self.request.user)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if FavoriteRecipe.objects.filter(user=request.user,
                                         recipe=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже есть в Избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe, many=False)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not FavoriteRecipe.objects.filter(user=request.user,
                                             recipe=recipe).exists():
            return Response(
                {'errors': 'В Избранном нет такого рецепта '},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(FavoriteRecipe, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe, many=False)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            return Response(
                {'errors': 'В списке покупок нет такого рецепта '},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(ShoppingCart, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartViewSet(APIView):
    def get(self, request):
        user = request.user
        recipes_list = ShoppingCart.objects.filter(user=user).values('recipe')
        recipes = Recipe.objects.filter(pk__in=recipes_list)
        shopping_list_dict = {}
        recipe_count = 0
        for recipe in recipes:
            recipe_count = recipe_count + 1
            ing_amounts_list = IngredientRecipe.objects.filter(recipe=recipe)
            for ing in ing_amounts_list:
                if ing.ingredient.name in shopping_list_dict:
                    shopping_list_dict[ing.ingredient.name][0] += ing.amount
                else:
                    shopping_list_dict[ing.ingredient.name] = [
                        ing.amount, ing.ingredient.measurement_unit
                    ]
        shop_string = (
            f'Отобрано рецептов: {recipe_count}\n\n'
            f'Необходимые ингредиенты:\n\n')
        for key, value in shopping_list_dict.items():
            shop_string += f'{key} ({value[1]}) - {str(value[0])}\n'
        response = HttpResponse(
            shop_string,
            content_type='text/plain, charset=utf8'
        )
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response


class FollowViewSet(ModelViewSet):
    serializer_class = SubscriptionsSerializer
    pagination_class = PaginationClass
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if Follow.objects.filter(user=request.user,
                                 author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(user=request.user, author=author)
        serializer = SubscriptionsSerializer(
            get_object_or_404(Follow, user=request.user,
                              author=author),
            many=False
        )
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        get_object_or_404(Follow, user=request.user,
                          author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
