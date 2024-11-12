from django.forms import DateTimeInput, ModelForm, Textarea
from django.utils import timezone

from .models import Comment, Post
from .validators import date_in_future


class PostForm(ModelForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if all((
            self.instance,
            self.instance.pub_date,
            self.instance.pub_date < timezone.now()
        )):
            self.fields['pub_date'].disabled = True

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if self.fields['pub_date'].disabled:
            return pub_date
        if pub_date is not None:
            date_in_future(pub_date)
        return pub_date


class CommentCreateForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': Textarea({'rows': '4'})
        }
