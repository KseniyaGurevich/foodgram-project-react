from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        verbose_name="Электронная почта",
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        verbose_name="Логин",
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
    )
    password = models.CharField(
        max_length=150,
        verbose_name="Пароль",
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name="Подписка"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    class Meta:
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name="Подписка"
    )
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name="Подписчик"
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self) -> str:
        return f"{self.author} {self.user}"
