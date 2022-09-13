from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()

NUMBER_OF_ENTRIES: int = 10


def select_paginator(request, selection, ):
    paginator = Paginator(selection, NUMBER_OF_ENTRIES)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request: HttpRequest) -> HttpResponse:
    """Обработчик запроса страницы - index()"""
    selection = Post.objects.select_related('author')
    page_obj = select_paginator(request, selection)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug: str):
    """Выводит шаблон с группами постов"""
    group = get_object_or_404(Group, slug=slug)
    selection = group.posts.all()
    page_obj = select_paginator(request, selection)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username: str):
    """Страница профайла пользователя."""
    author = get_object_or_404(User, username=username)
    selection = author.posts.all()
    page_obj = select_paginator(request, selection)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'following': following,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    """страница для публикации постов."""
    if request.method == 'POST':
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm(request.FILES or None)
    return render(request, 'posts/create_post.html', {'form': form})


def post_detail(request, post_id: int):
    """Страница для просмотра отдельного поста."""
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    form = CommentForm()
    context = {'author': author,
               'post': post,
               'form': form}
    return render(request, 'posts/post_details.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту"""
    get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post_id
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'core/404.html', {'path': request.path}, status=404)


@login_required
def post_edit(request, post_id: int):
    """страница редактирования постов"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def follow_index(request):
    """Новая запись пользователя появляется в ленте
    тех, кто на него подписан и не появляется в ленте тех
    кто не подписан."""
    selection = Post.objects.select_related(
        'author', 'group').filter(
        author__following__user=request.user)
    page_obj = select_paginator(request, selection)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Авторизованный пользователь может
    подписываться на других пользователей"""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Авторизованный пользователь может отписываться от пользователей"""
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:follow_index')
