from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .utilities import get_paginator_posts


@cache_page(20, key_prefix='index_page')
def index(request):
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': get_paginator_posts(
            request,
            Post.objects.select_related('author', 'group')
        ),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(
        Group.objects.select_related(),
        slug=slug
    )
    context = {
        'group': group,
        'page_obj': get_paginator_posts(
            request,
            group.posts.select_related('author')
        ),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(
        User.objects.select_related(),
        username=username
    )
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user))
    context = {
        'author': author,
        'following': following,
        'page_obj': get_paginator_posts(
            request,
            author.posts.select_related('group'),
        ),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    form = CommentForm(request.POST or None)
    comments = (Comment.objects
                       .select_related('post', 'author')
                       .filter(post_id=post.id))
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    user = request.user
    if not form.is_valid():
        return render(request, 'posts/create.html', {'form': form, })
    post = form.save(commit=False)
    post.author = user
    post.save()
    return redirect('posts:profile', user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )

    if post.author != request.user:
        raise Http404

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(
            request,
            'posts/create.html',
            {'form': form, 'is_edit': True, },
        )
    form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    context = {
        'page_obj': get_paginator_posts(
            request,
            Post.objects.select_related('author', 'group').filter(
                author_id__in=Follow.objects.filter(user=request.user)
                                    .values_list('author', flat=True))
        ),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(
        User.objects.select_related(),
        username=username
    )
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(
        User.objects.select_related(),
        username=username
    )
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect('posts:profile', username=username)
