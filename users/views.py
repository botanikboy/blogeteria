from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .forms import CustomUserCreationForm, CustomUserChangeForm
from blog.models import Post

User = get_user_model()


class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'users/registration_form.html'


class UserChangeView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/profile_form.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(User, pk=kwargs['pk'])
        if instance != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'users:profile', kwargs={'username': self.request.user.username})


def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        posts = Post.objects.filter(
            author=user).select_related('category', 'location', 'author'
                                        ).prefetch_related('comments')
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True).select_related(
                'category', 'location', 'author'
                ).prefetch_related('comments')
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'page_obj': page_obj,
    }
    return render(request, 'users/profile.html', context)
