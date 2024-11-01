from django.core.exceptions import ValidationError
from django.utils import timezone


def date_in_future(value) -> None:
    if value < timezone.now():
        raise ValidationError(
            'Дата и время должны быть в будущем'
        )
