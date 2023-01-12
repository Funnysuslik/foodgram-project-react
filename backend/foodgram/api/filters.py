from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag, User


class IngredientFilter(filters.FilterSet):
    """Просто фильтр оп имени.
    В будущем омжно сделать выдачу по лучшему совпадению?"""

    name = filters.CharFilter(
        method='filter_name', field_name='name')

    def filter_name(self, queryset, field_name, value):
        if value != "":
            value = value.lower()
            return queryset.filter(name__contains=value)

        return queryset


class RecipeFilter(filters.FilterSet):
    """
    Простой фильтр по автору и тэгам.
    Доп поля:
     - добавлено в избраное
     - подписан на автора
    """

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='author',
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
        field_name='favorite__recipe'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    def get_is_favorited(self,  queryset, field_name, value):

        return queryset.filter(favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, field_name, value):

        return queryset.filter(shopping_cart__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
