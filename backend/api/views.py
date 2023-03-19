from django.conf import settings
from rest_framework import generics, status, viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from api.permissions import (
    AuthorOrAdminOrReadOnly,
    AdminOrReadOnly
    )
from rest_framework.permissions import(
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import PaginationClass

from .serializers import (
    RecipeSerializer,
    RecipeReadSerializer,
    ShowFollowSerializer,
    TagSerializer,
    IngredientsSerializer,
    FavoriteRecipeSerializer,
    ShoppingCartSerializer,
    UserMeSerializer,
    FollowSerializer,
    UserSerializer,
)

from recipe.models import (
    Recipe,
    Tag,
    Ingredients,
    IngredientRecipe,
    FavoriteRecipe,
    ShoppingCart
)
from users.models import Follow, User

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AdminOrReadOnly,)

class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all().order_by('id')
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AdminOrReadOnly,)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).order_by('author')
    serializer_class = RecipeSerializer
    pagination_class = PaginationClass
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AddDeleteFavoriteRecipe(
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView
):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = (AllowAny,)
    pagination_class = PaginationClass
    queryset = FavoriteRecipe.objects.all().order_by('recipe')

    def get_object(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        self.check_object_permissions(self.request, recipe)
        return recipe

    def create(self, request, *args, **kwargs):
        shop_card = FavoriteRecipe.objects.create(
            user=request.user,
            recipe=self.get_object()
        )
        serializer = FavoriteRecipeSerializer(
            shop_card,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        resipe_del = FavoriteRecipe.objects.filter(
            recipe=self.get_object()
        )
        resipe_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddDeleteShoppingCart(
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView,
):
    pagination_class = PaginationClass
    queryset = ShoppingCart.objects.all().order_by('recipe')
    serializer_class = ShoppingCartSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        self.check_object_permissions(self.request, recipe)
        return recipe

    def post(self, request, *args, **kwargs):
        shop_card = ShoppingCart.objects.create(
            user=request.user,
            recipe=self.get_object()
        )
        serializer = ShoppingCartSerializer(
            shop_card,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        resipe_del = ShoppingCart.objects.filter(
            recipe=self.get_object()
        )
        resipe_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
#        permission_classes=(IsAuthenticated,)
    )
    def get_patch_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserMeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserMeSerializer(user,
                                      data=request.data,
                                      partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post']


class FollowApiView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    pagination_class = PaginationClass
    def post(self, request, *args, **kwargs):
        if Follow.objects.filter(
            author=get_object_or_404(
                User, pk=kwargs.get('id', None)
            ),
            user=request.user
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj_follow = Follow(author=get_object_or_404(
                User,
                pk=kwargs.get('id', None)
            ),
            user=request.user
        )
        obj_follow.save()

        serializer = ShowFollowSerializer(
            get_object_or_404(
                User, pk=kwargs.get('id', None)
            ),
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
            Follow,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ShowFollowSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_cart__user=request.user
    ).order_by('ingredient__name').values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    for ingredient in ingredients:
        ingredient_list += (
            f"\n{ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']}) - "
            f"{ingredient['amount']}"
        )
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
    return response