from django.core import validators
from django.db import models

from colorfield.fields import ColorField
from users.models import User


class Tag(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    colorcode = ColorField(unique=True)
    slug = models.SlugField(unique=True, verbose_name="Идентификатор")


class Ingredients(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    measurement = models.IntegerField(verbose_name="Измерение")


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="автор",
    )
    title = models.CharField(max_length=200, verbose_name="Название")
    image = models.ImageField(
        "Картинка", upload_to="static/recipe/", blank=True
    )
    description = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name="recipe",
        verbose_name="ингредиенты",
    )
    tag = models.ManyToManyField(
        Tag,
        related_name="recipe",
        verbose_name="Тег",
    )
    time = models.DateTimeField(verbose_name="Время приготовления")


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name="ingredient",
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            validators.MinValueValidator(
                1, message="Минимальное число единиц - 1"
            ),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique ingredient"
            )
        ]


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites_recipe",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"], name="unique recipe"
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт для покупки",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления",
    )

    class Meta:
        ordering = ("-recipe",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]
