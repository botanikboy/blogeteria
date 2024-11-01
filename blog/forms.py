from django.forms import DateTimeInput, ModelForm

from .models import Post
from .validators import date_in_future


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

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date is not None:
            date_in_future(pub_date)
        return pub_date
