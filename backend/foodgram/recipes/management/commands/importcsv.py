"""Filler."""
from csv import DictReader
from json import load
from django.core.management.base import BaseCommand

from recipes.models import (
    Ingredient
)


class Command(BaseCommand):
    """Importing csv file in local db."""

    help = (
        'Import list of files from static/data/:'
        + 'category.csv, comment.csv, genre.csv, genre_title.csv, review.csv,'
        + ' title.csv and user.csv'
    )

    def handle(self, *args, **option):
        """Filler."""
        print("Loading DB data")
        dictin = load(open('./data/ingredients.json', encoding='utf-8'))

        for row in dictin:
            ingredient = Ingredient.objects.get_or_create(
                name=row['name'],
                measurement_unit=row['measurement_unit'],
            )
            print(ingredient)

        print('Ingredients done..')
        print('DB filled')
