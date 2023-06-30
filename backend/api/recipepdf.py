#со шрифтами разберусь при деплое на сервер

from io import BytesIO

from django.http import FileResponse
from recipes.models import RecipeIngredientsMerge
from reportlab.pdfgen import canvas


def recipe_pdf_download(request):
    ingredients = RecipeIngredientsMerge.objects.filter(
        recipe__shopping__user=request.user,
    ).values_list(
        'ingredient__name', 'ingredient__measurement_unit', 'amount',
    )
    cart_list = {}
    for item in ingredients:
        name = item[0]
        if name not in cart_list:
            cart_list[name] = {
                'measurement_unit': item[1],
                'amount': item[2],
            }
        else:
            cart_list[name]['amount'] += item[2]

    buffer = BytesIO()
    page = canvas.Canvas(buffer)
    height = 900
    for i, (name, data) in enumerate(cart_list.items(), start=1):
        page.drawString(
            90, height, f"{i}. {name} – {data['amount']} {data['measurement_unit']}"
        )
        height -= 30
    page.save()
    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True, filename='recipe_list.pdf'
    )
