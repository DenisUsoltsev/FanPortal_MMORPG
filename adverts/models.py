from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.html import strip_tags


def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya', ' ': '_'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Advert.Status.PUBLISHED)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=70, unique=True, db_index=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})


class Advert(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, unique=True, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="Slug")
    text = RichTextUploadingField(verbose_name='Содержание объявления')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(choices=Status.choices, default=Status.DRAFT, verbose_name="Статус")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts', verbose_name='Категории')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='posts', verbose_name='Автор')

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def preview(self):
        result = strip_tags(self.text)
        return f'{result[:150]}...'

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(translit_to_eng(self.title))
        super().save(*args, **kwargs)


class Response(models.Model):
    class Status(models.IntegerChoices):
        CHECK = 0, 'Проверяется'
        ACCEPTED = 1, 'Принято'

    text = models.TextField(verbose_name='Отклик')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE, related_name='response', verbose_name='Объявление')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='averts', verbose_name='Автор')
    is_accepted = models.BooleanField(choices=Status.choices, default=Status.CHECK, verbose_name="Статус")

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def preview(self):
        result = strip_tags(self.text)
        return f'{result[:200]}...'

    def get_absolute_url(self):
        return reverse('response', kwargs={'pk': self.id})

    def __str__(self):
        return self.text


class Subscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='subscriptions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subscriptions')

    class Meta:
        unique_together = ('user', 'category')  # Запрещаем повторную подписку на ту же категорию
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f'{self.user.username} подписан на {self.category.name}'
