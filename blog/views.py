from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.utils import timezone

from .models import Post, Category


def index(request):
    posts_list = Post.objects.filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True
    ).select_related('category', 'location')[:10]
    context = {'posts': posts_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        ).select_related('location', 'category'),
        pk=pk
    )
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug
    )
    posts = get_list_or_404(
        Post.objects.filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        ).select_related('location', 'category'),
        category=category
    )
    context = {'posts': posts, 'category': category}
    return render(request, 'blog/category.html', context)
