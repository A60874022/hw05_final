from django.forms import ModelForm

from .models import Comment, Follow, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class FollowForm(ModelForm):
    class Meta:
        model = Follow
        labels = {'user': 'Подписка на:', 'author': 'Автор записи'}
        fields = ['user']
