import io
import os

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .serializers import IngredientWithAmountSerializer
from recipes.models import IngredientAmount, Recipe


def make_pdf(data, filename, http_status):
    """
    Не красиво, но хотя бы как-то выдаёт респонс файлом.
    """
    pdfmetrics.registerFont(TTFont(
        'DejaVuSansCondensed',
        os.path.join(os.path.dirname(
            os.path.abspath(__file__)),
            'DejaVuSansCondensed.ttf'
        )
    ))

    all_ingredients = {}

    width, height = A4
    height -= 20
    buffer = io.BytesIO()

    pdf_file = canvas.Canvas(buffer, pagesize=A4)
    pdf_file.setFont('DejaVuSansCondensed', 11)

    pdf_file.drawString(width / 2 - 20, height, 'Мой список покупок')
    height -= 20

    for recipe_in_cart in data:
        recipe = Recipe.objects.get(id=recipe_in_cart.pop('recipe'))
        ingredients = IngredientWithAmountSerializer(
            IngredientAmount.objects.filter(recipe=recipe),
            many=True
        ).data
        for ingredient in ingredients:
            name = ingredient.pop('name')
            amount = ingredient.pop('amount')
            unit = ingredient.pop('measurement_unit')
            if name in all_ingredients:
                all_ingredients[name][0] += amount
            else:
                all_ingredients[name] = [amount, unit]

    for ingredient in all_ingredients:
        pdf_file.drawString(
            10,
            height,
            '{name} - {amount} {unit}'.format(
                name=ingredient,
                amount=all_ingredients[ingredient][0],
                unit=all_ingredients[ingredient][1]
            )
        )
        height -= 10

    pdf_file.showPage()
    pdf_file.save()
    buffer.seek(0)
    response = HttpResponse(
        content=buffer,
        content_type='application/pdf',
        status=http_status
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
