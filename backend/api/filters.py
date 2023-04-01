import django_filters as filters
from recipe.models import Recipe, Tag
from users.models import User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_in_shopping_cart = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(), label="В корзине!"
    )
    favorites_recipe = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(), label="В избранных."
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset = Tag.objects.all(),
        field_name = 'tags_slug',
        to_field_name = 'slug'
    )

    class Meta:
        model = Recipe
        fields = ["favorites_recipe", "is_in_shopping_cart", "author", "tags"]
