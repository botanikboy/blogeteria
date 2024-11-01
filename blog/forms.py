from django.forms import ModelForm, DateTimeInput

from .models import Post


class PostCreateForm(ModelForm):

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image',
        ]
        widgets = {
            'pub_date': DateTimeInput({
                'type': 'datetime-local',
                'style': 'width:200px',
            })
        }
