from email.headerregistry import Group
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):

    title = models.CharField("page title", max_length=200)
    slug = models.SlugField("group name", unique=True)
    description = models.TextField("group description")

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста')
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True,
        db_index=True,)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        )
    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True, null=True,
        related_name="posts",
        )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField('Текст комментария')
    created = models.DateTimeField(
        'Дата и время публикации комментария',
        auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='following',
    )
