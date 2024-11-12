from django.contrib.auth import get_user_model
from django.db import models
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
        blank=True,
        on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        null=True,
        blank=True,
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
        return (f'{self.author}: {self.title[:10]}'
                f'{"..." if len(self.title) > 10 else ""}')

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


class Comment(PublishedModel):
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    is_edited = models.BooleanField(
        'Отметка о редактировании',
        default=False,
    )
    date_edited = models.DateTimeField(
        'Время редактирования',
        auto_now=True
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'{self.author} к посту {self.post}'
                f' от {self.created_at.strftime("%Y-%m-%d %H:%M")}')

    @property
    def days_from_publish(self):
        time = timezone.now() - self.created_at
        return time.days
