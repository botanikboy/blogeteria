from django.views.generic import CreateView, TemplateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm

User = get_user_model()


class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'users/registration_form.html'


class UserProfile(TemplateView):
    template_name = 'users/profile.html'
