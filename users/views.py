from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm
from blog.models import Post

User = get_user_model()


class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'users/registration_form.html'


def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=user).select_related('category', 'location')
    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'users/profile.html', context)
