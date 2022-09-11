from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Возвращает страницу «Об авторе»."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Возвращает страницу «Технологии»."""
    template_name = 'about/tech.html'
