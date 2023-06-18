import io

from django.http import FileResponse
from reportlab.pdfgen import canvas


def recipe_pdf_download(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    width, height = p._pagesize

    title = "Список рецептов"
    title_font_size = 18

    title_width = p.stringWidth(title, size=title_font_size)
    title_height = p._leading * title_font_size

    x = (width - title_width) / 2
    y = height - title_height - 50

    p.setFont("Helvetica-Bold", title_font_size)
    p.drawString(x, y, title)
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True, filename='recipekorzina.pdf',
    )
