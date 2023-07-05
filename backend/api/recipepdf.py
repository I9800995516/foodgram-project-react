from io import BytesIO

from api.serializers import RecipeIngredientsMerge
from django.http import FileResponse
from recipes.models import Cart
from reportlab.lib import colors, pagesizes
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

FONT_PATH = 'static/robotor.ttf'
PAGE_WIDTH, PAGE_HEIGHT = pagesizes.A4
MARGIN = 50
BODY_X, BODY_Y = MARGIN, MARGIN
BODY_WIDTH, BODY_HEIGHT = PAGE_WIDTH - 2 * MARGIN, PAGE_HEIGHT - 2 * MARGIN
TITLE_X, TITLE_Y = MARGIN, PAGE_HEIGHT - MARGIN - 20
PAGE_FONT_SIZE = 13
TITLE_FONT_SIZE = 16
RECIPE_NAME_FONT_SIZE = 14
TITLE_BOTTOM_SPACE = 80
INGREDIENT_NUMBER_INDENT = 30
INGREDIENT_LINE_HEIGHT = 15
INGREDIENT_SPACE_AFTER = 20
INGREDIENT_SPACE_BEFORE = 0
INGREDIENT_LEADING = 12


def recipe_pdf_download(request):
    shopping_cart = Cart.objects.filter(user=request.user)
    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('robotor', FONT_PATH))
    page = canvas.Canvas(buffer, pagesize=pagesizes.A4)

    # Установка фона всей страницы
    page.setFillColor(colors.darkorange)
    page.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
    page.setFillColor(colors.black)

    # Установка параметров заголовка
    title_style = ParagraphStyle(
        name='Title',
        fontName='robotor',
        fontSize=TITLE_FONT_SIZE,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=0,
        leading=16,
        fontWeight='bold',
    )
    title_paragraph = Paragraph(
        'Список ингредиентов для выбранных рецептов',
        title_style,
    )
    title_paragraph.wrapOn(page, BODY_WIDTH, BODY_HEIGHT)
    title_paragraph.drawOn(page, TITLE_X, TITLE_Y)

    # Цвет фона
    page.setFillColor(colors.darkorange)
    page.rect(
        BODY_X, BODY_Y, BODY_WIDTH,
        BODY_HEIGHT - TITLE_BOTTOM_SPACE, fill=True, stroke=False,
    )
    page.setFillColor(colors.black)
    page.setFont('robotor', PAGE_FONT_SIZE)
    height = BODY_Y + BODY_HEIGHT - TITLE_BOTTOM_SPACE

    for shopping_item in shopping_cart:
        recipe = shopping_item.recipe
        recipe_name = recipe.name

        ingredients = RecipeIngredientsMerge.objects.filter(
            recipe=recipe).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount',
        )

        # Отображение названия рецепта
        recipe_name_style = ParagraphStyle(
            name='RecipeName',
            fontName='robotor',
            fontSize=RECIPE_NAME_FONT_SIZE,
            textColor=colors.black,
            spaceAfter=20,
            spaceBefore=0,
            leading=16,
        )
        recipe_name_paragraph = Paragraph(
            f'<b>Рецепт:</b> {recipe_name}',
            recipe_name_style,
        )
        recipe_name_paragraph.wrapOn(page, BODY_WIDTH, BODY_HEIGHT)
        recipe_name_paragraph.drawOn(page, TITLE_X, height)
        height -= INGREDIENT_SPACE_AFTER

        # Отображение ингредиентов рецепта
        for i, (
            name, measurement_unit, amount,
        ) in enumerate(ingredients, start=1):
            ingredient_style = ParagraphStyle(
                name='Ingredient',
                fontName='robotor',
                fontSize=PAGE_FONT_SIZE,
                textColor=colors.black,
                spaceAfter=INGREDIENT_SPACE_AFTER,
                spaceBefore=INGREDIENT_SPACE_BEFORE,
                leading=INGREDIENT_LEADING,
            )
            ingredient_text = f'{i}. {name} – {amount} {measurement_unit}'
            ingredient_paragraph = Paragraph(ingredient_text, ingredient_style)
            ingredient_paragraph.wrapOn(
                page, BODY_WIDTH - INGREDIENT_NUMBER_INDENT, BODY_HEIGHT)
            ingredient_paragraph.drawOn(
                page, BODY_X + INGREDIENT_NUMBER_INDENT, height)
            height -= INGREDIENT_LINE_HEIGHT

        height -= INGREDIENT_SPACE_AFTER

    page.showPage()
    page.save()
    buffer.seek(0)

    return FileResponse(
        buffer, as_attachment=True, filename='shopping_list.pdf')
