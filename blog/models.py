from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import PublishedModel

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тематическая категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self) -> str:
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'Географическая метка'
        verbose_name_plural = 'Метки'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок')
    text = models.TextField(
        verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Если установить дату и время в будущем — можно делать'
                  ' отложенные публикации.',
        default=timezone.now,
        blank=True, null=True)
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
    image = models.ImageField(
        'Картинка',
        upload_to="uploads/%Y/",
        blank=True,
        null=True,
        )

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.author}: {self.title}'

    def save(self, *args, **kwargs):
        if not self.pub_date:
            self.pub_date = timezone.now()
        super().save(*args, **kwargs)

    @property
    def days_to_publish(self):
        time = self.pub_date - timezone.now()
        if time.days >= 0:
            return time.days
        return -1
