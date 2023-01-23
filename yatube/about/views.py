from django.views.generic.base import TemplateView
# from django.shortcuts import render


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = {
            'Python': 85,
            'Django': 60,
            'JavaScript': 70,
            'Vue': 60,
            'Верстка': 90,
        }
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Технологии'
        context['techs'] = (
            {
                'name': 'language',
                'title': 'Язык программирования',
                'text': """
                <h2>Python</h2>
                <p>Оформление кода PEP8</p>
                <p>С использованием объектно-ориентированным
                    программированием</p>
                <p>Замыкания</p>
                <p>Декораторы</p>
                """
            },
            {
                'name': 'framework',
                'title': 'Framework',
                'text': """
                <h2>Django</h2>
                <p>Архитектура MVC (Model-View-Controller)</p>
                <p>Использование встроенного интерфейса администратора</p>
                <p>Django ORM</p>
                <p>Расширяемая система шаблонов</p>
                <p>Маршрутиризация URLs</p>
                <p>Авторизация и аутентификация</p>
                <p>Работы с формами</p>
                <p>Система кеширования</p>
                <p>Использование инструмента django-debug-toolbar</p>
                """
            },
            {
                'name': 'databases',
                'title': 'База данных',
                'text': """
                <h2>SQLite3, Django ORM</h2>
                <p>Запросы, используя ORM</p>
                <p>Оптимизация запросов.
                Испрользование select_related() и prefetch_related()</p>
                <p>Кэширование</p>
                """
            },
            {
                'name': 'testing',
                'title': 'Тестирование',
                'text': """
                <h2>Unittest</h2>
                <p>Структура файлов для соответствующих тестов</p>
                <p>Написание тестов</p>
                <p>Проверка моделей, urls, контекта, форм.</p>
                """
            },
            {
                'name': 'layout',
                'title': 'Верстка',
                'text': """
                <h2>Верстка</h2>
                <p>HTML, CSS, JS</p>
                <h2>Bootstrap</h2>
                <p>Использование сетки</p>
                <p>Множество компонентов</p>
                """
                # 'include': 'about/parts/tech-layout.html',
            },
            {
                'name': 'deploy',
                'title': 'Развертывание',
                'text': """
                <h2>pythonanywhere.com</h2>
                <p>Развертывание сайта на pythonanywhere.com</p>
                """
            },
        )
        return context
