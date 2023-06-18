from django.contrib.auth.validators import UnicodeUsernameValidator


class UsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\w.@+-]+$'
    flags = 0
    message = (
        'Уникальный юзернейм. '
        'В имени пользователя допускаются следующие символы: '
        'буквы (a-z, A-Z), '
        'цифры (0-9), '
        'подчеркивание (_), '
        'точка (.), '
        'собака (@), '
        'знак плюса (+), '
        'и тире (-). '
        'Не допускаются символы: #, $, % и пробелы.'
    )
