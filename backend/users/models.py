from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import (
    validate_user,
    UserValidator,
)

NAME_LENGTH = 150
MAIL_LENGTH = 254


class UserRole:
    USER = 'user'
    ADMIN = 'admin'
    choices = [
        (USER, 'USER'),
        (ADMIN, 'ADMIN'),
    ]


class User(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=NAME_LENGTH)
    last_name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Фамилия')
    email = models.EmailField(
        max_length=MAIL_LENGTH,
        verbose_name='email',
        unique=True)
    username = models.CharField(
        verbose_name='username',
        max_length=NAME_LENGTH,
        unique=True,
        validators=(validate_user, UserValidator()),
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follower(models.Model):
    """Модель подписки на автора."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Автор')

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow_constraint',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_follow_constraint',
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
