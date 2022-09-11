from django.utils import timezone


def year(request) -> int:
    """Добавляет переменную с текущим годом."""
    time = timezone.now().year
    return {
        'year': time,
    }
