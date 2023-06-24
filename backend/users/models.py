from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from foodgram.settings import EMAIL_LENGTH, NAME_LENGTH

from .validators import UsernameValidator


class User(AbstractUser):
    """Модель создания пользователя."""

    USER = 'user'
    ADMIN = 'admin'

    USER_ROLES = [
        (USER, 'user'),
        (ADMIN, 'admin'),
    ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    username_validade = UsernameValidator()
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField('Имя',
                                  max_length=NAME_LENGTH,
                                  blank=True,
                                  )
    last_name = models.CharField('Фамилия',
                                 max_length=NAME_LENGTH,
                                 blank=True,
                                 )
    username = models.CharField(
        max_length=NAME_LENGTH,
        unique=True,
        validators=[username_validade],
        verbose_name='Username')

    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=20,
        choices=USER_ROLES,
        default='user',
    )

    @property
    def is_admin(self):
        """Проверка пользователя на наличие прав администратора."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_user(self):
        """Проверка пользователя на наличие стандартных прав."""
        return self.role == self.USER

    @property
    def following(self):
        """Получение списка пользователей, на которых подписан."""
        return User.objects.filter(follower__author=self)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
            'email',
        )

    def __str__(self):
        return self.username[:15]


class Follow(models.Model):
    """Модель подписчика."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow',
            ),
            models.CheckConstraint(check=~Q(user=F('author')),
                                   name='following'),
        ]

    def __str__(self):
        return f'{self.user.username[:20]} follows {self.author.username[:20]}'
