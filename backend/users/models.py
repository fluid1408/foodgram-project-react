from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username, validate_year

class User(AbstractUser):
    email = models.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        'имя',
        max_length=settings.NAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'фамилия',
        max_length=settings.NAME_MAX_LENGTH,
        blank=True
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff


    class Meta:
        ordering = ('username',)

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_following"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def str(self):
        return f"{self.user.username}-{self.author.username}"
