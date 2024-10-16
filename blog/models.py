from django.db import models
from django.contrib.auth import get_user_model

from core.models import PublishedModel

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тематическая категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)


class Location(PublishedModel):
    name = models.CharField(
        max_length=256,
    )

    class Meta:
        verbose_name = 'Географическая метка'
        verbose_name_plural = 'Метки'
        ordering = ('name',)


class Post(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Пост')
    text = models.TextField(
        verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE)
    location = models.ForeignKey(
        Location,
        verbose_name='Место',
        null=True,
        on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        null=True,
        on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('pub_date',)
