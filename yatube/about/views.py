from django.views.generic.base import TemplateView
# from django.shortcuts import render


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Технологии'
        context['techs'] = (
            {
                'name': 'language',
                'title': 'Язык программирования',
                'text': 'Python'
            },
            {
                'name': 'framework',
                'title': 'Framework',
                'text': 'Django'
            },
            {
                'name': 'databases',
                'title': 'База данных',
                'text': 'SQLite3'
            },
            {
                'name': 'layout',
                'title': 'Верстка',
                'text': '<h2>html, css, js</h2>'
            },
        )
        return context
