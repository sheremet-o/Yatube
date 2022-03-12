from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


PAGE_PER_LIST = 10


#  Главная страница
@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGE_PER_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, PAGE_PER_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile_name = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_name)
    post_count = posts.count()
    paginator = Paginator(posts, PAGE_PER_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=profile_name).exists()
    context = {
        'page_obj': page_obj,
        'profile_name': profile_name,
        'post_count': post_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_number = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author=post_number.author).count()
    post_title = post_number.text[:30]
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post_number': post_number,
        'post_count': post_count,
        'post_title': post_title,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not post.author == request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    context = {
        'is_edit': True,
        'form': form,
        'post': post}
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:post_detail', post_id=post_id)


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
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return render(request, 'posts/index.html')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return render(request, 'posts/index.html')


@login_required
def follow_index(request):
    authors_ids = Follow.objects.filter(
        user=request.user).values_list('author', flat=True)
    posts = Post.objects.filter(author__in=authors_ids)
    paginator = Paginator(posts, PAGE_PER_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)
