from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.utils import timezone

from .models import Post, Category


def index(request):
    posts = Post.objects.filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True
    ).select_related('category', 'location')
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        }
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
        ).select_related('location', 'category', 'author'),
        category=category
    )
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
        }
    return render(request, 'blog/category.html', context)
