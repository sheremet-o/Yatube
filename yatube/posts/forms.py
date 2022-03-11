# from attr import fields
from django import forms
from .models import Post, Comment
from django.utils.translation import ugettext_lazy as _


# Класс для формы создания поста
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст поста'),
            'group': _('Группа'),
        }
        help_texts = {
            'text': _('введите текст поста'),
            'group': _('укажите группу, к которой относится пост'
                       '(необязательное поле)')
        }


# Форма для добавления комментария к посту
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Текст комментария')
        }
