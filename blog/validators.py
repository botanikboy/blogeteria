from django.utils import timezone

from django.core.exceptions import ValidationError


def date_in_future(value) -> None:
    if value < timezone.now():
        raise ValidationError(
            'Дата и время должны быть в будущем'
        )
