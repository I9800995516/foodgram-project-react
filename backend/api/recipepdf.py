from collections import defaultdict
from io import BytesIO

from django.db import models
from django.http import FileResponse
from reportlab.lib import colors, pagesizes
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from api.serializers import RecipeIngredientsMerge
from recipes.models import Cart


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
QUANTITY = 1000


def format_quantity(quantity, measurement_unit):
    if measurement_unit == 'г':
        if quantity >= QUANTITY:
            quantity /= QUANTITY
            measurement_unit = 'кг'
    elif measurement_unit == 'шт':
        measurement_unit = 'штук'
    return quantity, measurement_unit


def recipe_pdf_download(request):
    shopping_cart = Cart.objects.filter(user=request.user)
    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('robotor', FONT_PATH))
    page = canvas.Canvas(buffer, pagesize=pagesizes.A4)

    page.setFillColor(colors.darkorange)
    page.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
    page.setFillColor(colors.black)

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
            recipe=recipe).values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(total_amount=models.Sum('amount'))

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

        for i, ingredient in enumerate(ingredients, start=1):
            ingredient_name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            total_amount = ingredient['total_amount']
            total_amount, measurement_unit = format_quantity(
                total_amount, measurement_unit)

            ingredient_style = ParagraphStyle(
                name='Ingredient',
                fontName='robotor',
                fontSize=PAGE_FONT_SIZE,
                textColor=colors.black,
                spaceAfter=INGREDIENT_SPACE_AFTER,
                spaceBefore=INGREDIENT_SPACE_BEFORE,
                leading=INGREDIENT_LEADING,
            )
            ingredient_text = (
                f'{i}. {ingredient_name} – {total_amount} '
                f'{measurement_unit}'
            )
            ingredient_paragraph = Paragraph(ingredient_text, ingredient_style)
            ingredient_paragraph.wrapOn(
                page, BODY_WIDTH - INGREDIENT_NUMBER_INDENT, BODY_HEIGHT)
            ingredient_paragraph.drawOn(
                page, BODY_X + INGREDIENT_NUMBER_INDENT, height)
            height -= INGREDIENT_LINE_HEIGHT

        height -= INGREDIENT_SPACE_AFTER

    ingredient_quantities = defaultdict(float)
    ingredient_measurement_units = {}
    for shopping_item in shopping_cart:
        recipe = shopping_item.recipe
        ingredients = RecipeIngredientsMerge.objects.filter(
            recipe=recipe).values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(total_amount=models.Sum('amount'))

        for ingredient in ingredients:
            ingredient_name = ingredient['ingredient__name']
            total_amount = ingredient['total_amount']
            total_amount, measurement_unit = format_quantity(
                total_amount, ingredient['ingredient__measurement_unit'])
            ingredient_quantities[ingredient_name] += total_amount
            ingredient_measurement_units[ingredient_name] = measurement_unit

    total_ingredients_title_style = ParagraphStyle(
        name='TotalIngredientsTitle',
        fontName='robotor',
        fontSize=RECIPE_NAME_FONT_SIZE,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=0,
        leading=16,
        fontWeight='bold',
    )
    total_ingredients_paragraph = Paragraph(
        'Общее количество ингредиентов',
        total_ingredients_title_style,
    )
    total_ingredients_paragraph.wrapOn(page, BODY_WIDTH, BODY_HEIGHT)
    total_ingredients_paragraph.drawOn(page, TITLE_X, height)
    height -= INGREDIENT_SPACE_AFTER

    for i, (ingredient_name, total_amount) in enumerate(
        ingredient_quantities.items(), start=1,
    ):

        measurement_unit = ingredient_measurement_units[ingredient_name]
        ingredient_style = ParagraphStyle(
            name='Ingredient',
            fontName='robotor',
            fontSize=PAGE_FONT_SIZE,
            textColor=colors.black,
            spaceAfter=INGREDIENT_SPACE_AFTER,
            spaceBefore=INGREDIENT_SPACE_BEFORE,
            leading=INGREDIENT_LEADING,
        )
        ingredient_text = (
            f'{i}. {ingredient_name} – {total_amount} {measurement_unit}')
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
        buffer, as_attachment=True, filename='shopping_list.pdf',
    )
