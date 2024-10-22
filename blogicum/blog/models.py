from django.db import models
from django.contrib.auth.models import User

from .constants import (
    MODEL_TITLE_MAX_LENGTH,
    MODEL_TITLE_VN,
    MODEL_DESCRIPTION_VERBOSE_NAME,
    MODEL_SLUG_VERBOSE_NAME,
    MODEL_SLUG_HELP_TEXT,
    MODEL_IS_PUBLISHED_VN,
    MODEL_IS_PUBLISHED_HELP_TEXT,
    MODEL_CREATED_AT_VN,
    MODEL_PUB_DATE_VERBOSE_NAME,
    MODEL_PUB_DATE_HELP_TEXT,
    MODEL_TEXT_VERBOSE_NAME,
    MODEL_AUTHOR_VERBOSE_NAME,
    MODEL_CATEGORY_VN,
    MODEL_LOCATION_VN,
    MODEL_NAME_VN,
    MODEL_TEXT_DISPLAY_MAX_LENGTH,
    MODEL_IMAGE_VERBOSE_NAME
)


class BaseModel(models.Model):
    is_published = models.BooleanField(default=True,
                                       verbose_name=MODEL_IS_PUBLISHED_VN,
                                       help_text=MODEL_IS_PUBLISHED_HELP_TEXT)
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=MODEL_CREATED_AT_VN)

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=MODEL_TITLE_MAX_LENGTH,
                             verbose_name=MODEL_TITLE_VN)
    description = models.TextField(verbose_name=MODEL_DESCRIPTION_VERBOSE_NAME)
    slug = models.SlugField(unique=True, verbose_name=MODEL_SLUG_VERBOSE_NAME,
                            help_text=MODEL_SLUG_HELP_TEXT)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=MODEL_TITLE_MAX_LENGTH,
                            verbose_name=MODEL_NAME_VN)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=MODEL_TITLE_MAX_LENGTH,
                             verbose_name=MODEL_TITLE_VN)
    text = models.TextField(verbose_name=MODEL_TEXT_VERBOSE_NAME)
    pub_date = models.DateTimeField(verbose_name=MODEL_PUB_DATE_VERBOSE_NAME,
                                    help_text=MODEL_PUB_DATE_HELP_TEXT)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name=MODEL_AUTHOR_VERBOSE_NAME,
                               related_name='posts')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True, verbose_name=MODEL_LOCATION_VN)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, verbose_name=MODEL_CATEGORY_VN,
                                 related_name='posts')
    image = models.ImageField(upload_to='posts_images', blank=True, null=True,
                              verbose_name=MODEL_IMAGE_VERBOSE_NAME)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return f'{self.text[:MODEL_TEXT_DISPLAY_MAX_LENGTH]}...' \
            if len(self.text) > MODEL_TEXT_DISPLAY_MAX_LENGTH else self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Комментарий автора {self.author} на пост {self.post}'
