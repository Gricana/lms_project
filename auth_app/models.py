from django.contrib.auth.models import AbstractUser
from django.db import models
from .functions import get_timestamp_path_user


class User(AbstractUser):
    username = models.CharField(max_length=10, unique=False)
    email = models.EmailField(unique=True, verbose_name='Email')
    birthday = models.DateField(verbose_name='Дата рождения', blank=False, null=True)
    description = models.TextField(verbose_name='Обо мне', null=True, blank=True, default='', max_length=200)
    avatar = models.ImageField(verbose_name='Фото', blank=True, upload_to=get_timestamp_path_user)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name_plural = 'Участники'
        verbose_name = 'Участник'
        ordering = ['last_name']

    def __str__(self):
        return f'Участник {self.first_name} {self.last_name}: {self.email}'
