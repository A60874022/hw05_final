from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

TEXT_LENGTH_LIMITER: int = 15

class Group(models.Model):
    """Создание модели для таблицы Сообщества."""
    title = models.CharField(max_length=200, verbose_name='Группа')
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name ='Текст поста',
        help_text = 'Dведите текст поста')

    pub_date = models.DateTimeField(
        verbose_name ='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name = 'Автор поста')
    group: None = models.ForeignKey(Group, on_delete=models.SET_NULL,
                                    related_name="posts", blank=True,
                                    null=True,
                                    verbose_name ='Название группы',
                                    help_text = 'Введите название группы'
                                    )
    image = models.ImageField(
        verbose_name = 'Картинка',
        upload_to='posts',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:TEXT_LENGTH_LIMITER]


class Comment(models.Model):
    """Создание модели для таблицы Комментарии."""
    text = models.TextField(
        verbose_name = 'Текст комментария',
        )
    created = models.DateTimeField(
        verbose_name = 'Дата публикации',
        auto_now_add=True)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')

    def __str__(self):
        return self.text[:TEXT_LENGTH_LIMITER]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')
