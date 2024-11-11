from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CommentCreateForm, PostCreateForm, PostEditForm
from .models import Category, Comment, Post


def index(request):
    posts = Post.objects.filter(
        Q(category__isnull=True) | Q(category__is_published=True),
        is_published=True,
        pub_date__lt=timezone.now()
    ).select_related('category', 'location', 'author')
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        }
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related(
            'location', 'category', 'author'),
        pk=pk
    )
    if request.user != post.author and (
        not post.is_published
        or (post.category is not None and not post.category.is_published)
        or post.pub_date > timezone.now()
    ):
        raise PermissionDenied
    form = CommentCreateForm()
    context = {
        'post': post,
    }
    if not request.user.is_anonymous:
        form = CommentCreateForm()
        context['form'] = form
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
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
        }
    return render(request, 'blog/category.html', context)


class PostMixing(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create_post.html'


class PostCreate(PostMixing, CreateView):
    form_class = PostCreateForm

    def get_success_url(self):
        return reverse_lazy(
            'users:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(PostMixing, UpdateView):
    form_class = PostEditForm

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != self.request.user:
            return redirect('blog:post_detail', pk=instance.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        if self.object.pub_date:
            initial['pub_date'] = self.object.pub_date.strftime(
                '%Y-%m-%dT%H:%M')
        return initial


class PostDelete(PostMixing, DeleteView):
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != self.request.user:
            return redirect('blog:post_detail', pk=instance.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/create_comment.html'


class CommentCreate(CommentMixin, CreateView):
    form_class = CommentCreateForm

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(
            Post, Q(category__isnull=True) | Q(category__is_published=True),
            pk=self.kwargs['pk'], is_published=True,
            pub_date__lt=timezone.now(),
        )
        form.instance.post = post
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['post'] = post
        return context


class CommentUpdate(CommentMixin, UpdateView):
    form_class = CommentCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        context['post'] = post
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_pk']}
        )

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            Q(post__category__isnull=True) | Q(
                post__category__is_published=True),
            pk=kwargs['pk'],
            post__is_published=True,
            post__pub_date__lt=timezone.now(),
        )
        if instance.author != self.request.user:
            return redirect('blog:post_detail', pk=self.kwargs['post_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.is_edited = True
        return super().form_valid(form)


class CommentDelete(CommentMixin, DeleteView):

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            Q(post__category__isnull=True) | Q(
                post__category__is_published=True),
            pk=kwargs['pk'],
            post__is_published=True,
            post__pub_date__lt=timezone.now(),
        )
        if instance.author != self.request.user:
            return redirect('blog:post_detail', pk=self.kwargs['post_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_pk']}
        )
