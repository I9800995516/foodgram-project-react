from io import BytesIO

from api.serializers import RecipeIngredientsMerge
from django.http import FileResponse
from recipes.models import RecipeKorzina
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def recipe_pdf_download(request):
    shopping_cart = RecipeKorzina.objects.filter(user=request.user)
    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('robotor', 'static/robotor.ttf'))
    page = canvas.Canvas(buffer)
    page.setFillColor(colors.lightseagreen)
    body_x, body_y = 50, 50
    body_width, body_height = 500, 700
    page.rect(body_x, body_y, body_width, body_height, fill=True, stroke=False)
    page.setFillColor(colors.black)
    page.setFont('robotor', 16)
    title_x, title_y = 100, 750
    page.drawString(
        title_x, title_y, 'Список ингредиентов для выбранных рецептов',
    )
    page.setFont('robotor', 13)
    height = body_y + body_height - 80
    for shopping_item in shopping_cart:
        recipe = shopping_item.recipe
        recipe_name = recipe.name
        ingredients = RecipeIngredientsMerge.objects.filter(
            recipe=recipe,
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount',
        )
        page.setFont('robotor', 14)
        page.drawString(title_x, height, f"Рецепт: {recipe_name}")
        height -= 20
        for i, (
            name, measurement_unit, amount,
        ) in enumerate(ingredients, start=1):
            page.drawString(
                body_x + 30,
                height, f'{i}. {name} – {amount} {measurement_unit}',
            )
            height -= 25
        height -= 20
    page.showPage()
    page.save()
    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True, filename='recipe_list.pdf',
    )
