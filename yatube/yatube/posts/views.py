from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Group, Post

NUMBER_OF_ENTRIES: int = 10


def index(request: HttpRequest) -> HttpResponse:
    """Обработчик запроса страницы - index()"""
    posts = Post.objects.order_by('-pub_date')[:NUMBER_OF_ENTRIES]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Обработчик запроса главной страницы - group_posts()"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.order_by('-pub_date')[:NUMBER_OF_ENTRIES]
    context = {'group': group, 'posts': posts}
    return render(request, "posts/group_list.html", context)
