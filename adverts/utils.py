menu = [{'title': "Объявления", 'url_name': 'posts'},
        {'title': "Поиск", 'url_name': 'search'},
        {'title': "Добавить объявление", 'url_name': 'add_post'},
        ]


class DataMixin:
    paginate_by = 5
    title_page = None
    cat_selected = None
    del_mode = None
    extra_context = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page

        if self.cat_selected is not None:
            self.extra_context['cat_selected'] = self.cat_selected

        if self.del_mode is not None:
            self.extra_context['del_mode'] = self.del_mode

    def get_mixin_context(self, context, **kwargs):
        context['cat_selected'] = None
        context.update(kwargs)
        return context
