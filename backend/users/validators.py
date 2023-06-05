from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.exceptions import ValidationError


def validate_user(value):
    if value == 'admin':
        raise ValidationError("Имя пользователя не может быть 'admin'!")


class UserValidator(UnicodeUsernameValidator):
    regex = r'^[\w.@+-]+\Z'
    flags = 0
    message = (
        'Имя пользователя может включать:'
        ' буквы, цифры '
        'и знаки @ . + -'
    )
