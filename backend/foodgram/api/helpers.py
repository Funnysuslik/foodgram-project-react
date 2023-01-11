from recipes.models import IngredientAmount


def set_tags_ingredients(recipe, ingredients, tags):
    ingredient_list = []
    recipe.tags.set(tags)

    for ingredient in ingredients:
        ingredient_list.append(IngredientAmount(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ))

    IngredientAmount.objects.bulk_create(ingredient_list)

    return recipe
