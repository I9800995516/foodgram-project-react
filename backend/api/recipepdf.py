from io import BytesIO

from django.http import FileResponse
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from api.serializers import RecipeIngredientsMerge
from recipes.models import Cart


FONT_PATH = 'static/robotor.ttf'
BODY_X, BODY_Y = 50, 50
BODY_WIDTH, BODY_HEIGHT = 500, 700
TITLE_X, TITLE_Y = 100, 750
PAGE_FONT_SIZE = 13
TITLE_FONT_SIZE = 16
RECIPE_NAME_FONT_SIZE = 14
TITLE_BOTTOM_SPACE = 80


def recipe_pdf_download(request):
    shopping_cart = Cart.objects.filter(user=request.user)
    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('robotor', FONT_PATH))
    page = canvas.Canvas(buffer)

    # Установка фона страницы
    page.setFillColor(colors.lightseagreen)
    page.rect(BODY_X, BODY_Y, BODY_WIDTH, BODY_HEIGHT, fill=True, stroke=False)
    page.setFillColor(colors.black)

    # Установка заголовка страницы
    page.setFont('robotor', TITLE_FONT_SIZE)
    page.drawString(
        TITLE_X, TITLE_Y, 'Список ингредиентов для выбранных рецептов')

    # Установка содержимого страницы
    page.setFont('robotor', PAGE_FONT_SIZE)
    height = BODY_Y + BODY_HEIGHT - TITLE_BOTTOM_SPACE

    # Предметы в корзине
    for shopping_item in shopping_cart:
        recipe = shopping_item.recipe
        recipe_name = recipe.name

        # Получение ингредиентов рецепта
        ingredients = RecipeIngredientsMerge.objects.filter(
            recipe=recipe).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount',
        )

        # Название рецепта
        page.setFont('robotor', RECIPE_NAME_FONT_SIZE)
        page.drawString(TITLE_X, height, f'Рецепт: {recipe_name}')
        height -= 20

        # Ингредиенты рецепта
        for i, (
            name, measurement_unit, amount,
        ) in enumerate(ingredients, start=1):
            page.drawString(
                BODY_X + 30,
                height,
                f'{i}. {name} – {amount} {measurement_unit}',
            )
            height -= 25

        height -= 20

    page.showPage()
    page.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='recipe_list.pdf')
