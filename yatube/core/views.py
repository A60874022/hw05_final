from django.shortcuts import render


def csrf_failure(request, reason=''):
    """Перенаправление в шаблон при получениии из-за
    ограничений в доступе для клиента"""
    return render(request, 'core/403csrf.html')


def page_not_found(request, exception):
    """Перенаправление в шаблон при ресурса по указанному URL"""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    """Перенаправление в шаблон при ошибках сервера"""
    return render(request, "core/500.html", status=500)
