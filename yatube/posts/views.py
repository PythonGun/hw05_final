from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

from yatube.settings import PAGE_NUM


def index(request):

    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    paginator = Paginator(posts, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'group_list.html'

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user).order_by('-pub_date')
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_number = paginator.count
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=user
        ).exists()
    else:
        following = None

    template = 'posts/profile.html'

    context = {
        'page_obj': page_obj,
        'author': user,
        'post_number': post_number,
        'post_list': post_list,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_num = post.author.posts.all().count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'post_num': posts_num,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
@csrf_exempt
def post_create(request):

    form = PostForm(request.POST or None)
    groups = Group.objects.all()
    template = 'posts/create_post.html'

    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    context = {
        'form': form,
        'groups': groups,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    groups = Group.objects.all()
    if form.is_valid():
        form = form.save(False)
        form.author = request.user
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
        'groups': groups,
    }
    form = PostForm({'text': post.text, 'group': post.group})
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    ).order_by('-pub_date')
    paginator = Paginator(posts, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=author)
