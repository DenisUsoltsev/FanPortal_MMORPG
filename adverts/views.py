from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Count, Case, When, IntegerField, Q
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from FanPortal_MMORPG import settings
from .forms import AddPostForm, AddResponseForm, SearchForm, ResponseSearchForm
from .models import Advert, Category, Response, Subscription
from .utils import DataMixin, menu


class AdvertsList(DataMixin, ListView):
    template_name = 'adverts/posts.html'
    context_object_name = 'posts'
    title_page = 'Объявления'
    cat_selected = 0

    def get_queryset(self):
        #return Advert.published.all().select_related('category')
        return Advert.published.annotate(response_count=Count(Case(
            When(response__is_accepted=True, then=1),
            output_field=IntegerField(),
        ))).select_related('category').order_by('-time_create')


class ShowPost(DataMixin, DetailView):
    template_name = 'adverts/post.html'
    title_page = 'Просмотр объявления'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = self.object.response.filter(is_accepted=True)
        return self.get_mixin_context(context)

    def get_object(self, queryset=None):
        return get_object_or_404(Advert.published, slug=self.kwargs[self.slug_url_kwarg])


class AddPost(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'adverts/add_post.html'
    title_page = 'Добавить объявление'
    success_url = reverse_lazy('user_posts')
    permission_required = 'adverts.add_advert'

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)


class EditPost(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, UpdateView):
    model = Advert
    fields = ['title', 'text', 'is_published', 'category']
    template_name = 'adverts/edit_del_post.html'
    success_url = reverse_lazy('posts')
    title_page = 'Редактировать объявление'
    context_object_name = 'post'
    del_mode = False
    permission_required = 'adverts.change_advert'


class DeletePost(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, DeleteView):
    model = Advert
    template_name = 'adverts/edit_del_post.html'
    success_url = reverse_lazy('user_posts')
    title_page = 'Удалить объявление'
    context_object_name = 'post'
    del_mode = True
    permission_required = 'adverts.delete_advert'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)


class ShowCategory(DataMixin, ListView):
    template_name = 'adverts/posts.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Advert.published.filter(category__slug=self.kwargs['cat_slug']).annotate(response_count=Count(Case(
        When(response__is_accepted=True, then=1),
        output_field=IntegerField(),
        ))).select_related("category").order_by('-time_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['posts']:
            category = context['posts'][0].category
            context['category'] = category
            context['is_subscribed'] = (self.request.user.is_authenticated and
                                        Subscription.objects.filter(user=self.request.user, category=category).exists())
        else:
            context = super().get_context_data(**kwargs)
            category = context['posts'][0].category

        return self.get_mixin_context(context,
                                  title='Категория - ' + category.name,
                                  cat_selected=category.pk)


class UserPosts(PermissionRequiredMixin, DataMixin, ListView):
    template_name = 'adverts/user_posts.html'
    context_object_name = 'user_posts'
    title_page = 'Объявления пользователя'
    permission_required = 'adverts.view_advert'
    cat_selected = 0

    def get_queryset(self):
        return Advert.objects.filter(author=self.request.user).annotate(response_count=Count(Case(
            When(response__is_accepted=True, then=1),
            output_field=IntegerField(),
        ))).select_related('category').order_by('-time_create')


class UserResponses(PermissionRequiredMixin, DataMixin, ListView):
    form_class = ResponseSearchForm
    template_name = 'adverts/user_responses.html'
    permission_required = 'adverts.view_response'
    cat_selected = 0

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET or None)
        results = None

        if form.is_valid():
            results = self.perform_search(form.cleaned_data)

        context = {
            'form': form,
            'responses': results,
            'title': 'Отклики пользователя',
        }
        return render(request, self.template_name, context)

    def perform_search(self, cleaned_data):
        queryset = Response.objects.all()

        search_type = cleaned_data.get('search_type')
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if search_type == 'user_responses':
            queryset = queryset.filter(author=self.request.user)
        elif search_type == 'responses':
            queryset = queryset.filter(advert__author=self.request.user)
        if title:
            queryset = queryset.filter(advert__title__icontains=title)
        if content:
            queryset = queryset.filter(text__icontains=content)
        if start_date:
            queryset = queryset.filter(time_create__gte=start_date)
        if end_date:
            queryset = queryset.filter(time_create__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ResponseSearchForm(self.request.GET)
        return context

    def post(self, request, *args, **kwargs):
        response_id = request.POST.get('response_id')
        response = get_object_or_404(Response, id=response_id)

        status_html = ''
        time_create = request.POST.get('time_create')
        author = request.POST.get('author')

        if 'accept' in request.POST:
            response.is_accepted = True
            response.save()

            recipient_email = response.author.email
            subject = 'Ваш отклик принят'
            message = f'Здравствуйте, {response.author.username}!\n\n' \
                      f'Ваш отклик на объявление "{response.advert.title}" был принят.\n' \
                      f'Поздравляем! Чтобы узнать больше деталей, перейдите на сайт.'

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )

            status_html = f'<p class="first">Статус: <i>Принято</i> | Автор: { author }</p><p class="last">дата: { time_create }</p>'

        elif 'decline' in request.POST:
            response.delete()
            status_html = f'<p class="first">Статус: <i>Проверяется</i> | Автор: { author }</p><p class="last">дата: { time_create }</p>'

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'status_html': status_html})

        return redirect(request.path_info)


class AddResponse(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddResponseForm
    template_name = 'adverts/response_add.html'
    title_page = 'Добавление отклика'
    success_url = reverse_lazy('posts')
    permission_required = 'adverts.add_response'

    def form_valid(self, form):
        advert_id = self.kwargs.get('pk')
        advert = get_object_or_404(Advert, pk=advert_id)

        response = form.save(commit=False)
        response.advert = advert
        response.author = self.request.user

        recipient_email = advert.author.email
        subject = 'Новый отклик на ваше объявление'
        message = f'Здравствуйте, {advert.author.username}!\n\n' \
                  f'Пользователь {self.request.user.username} оставил отклик на ваше объявление "{advert.title}".\n' \
                  f'Перейдите на сайт, чтобы просмотреть детали.'

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )

        return super().form_valid(form)


class ShowResponse(DataMixin, DetailView):
    model = Response
    template_name = 'adverts/response.html'
    title_page = 'Отклик'
    context_object_name = 'response'


class EditResponse(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, UpdateView):
    model = Response
    fields = ['text']
    template_name = 'adverts/edit_del_response.html'
    success_url = reverse_lazy('user_responses')
    title_page = 'Редактирование отклика'
    context_object_name = 'response'
    del_mode = False
    permission_required = 'adverts.change_response'


class DeleteResponse(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, DeleteView):
    model = Response
    template_name = 'adverts/edit_del_response.html'
    success_url = reverse_lazy('user_responses')
    title_page = 'Удаление отклика'
    context_object_name = 'response'
    del_mode = True
    permission_required = 'adverts.delete_response'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)


class SearchView(DataMixin, ListView):
    form_class = SearchForm
    template_name = 'adverts/search.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET or None)
        results = None

        if form.is_valid():
            search_type = form.cleaned_data['search_type']
            query = form.cleaned_data['query']
            author = form.cleaned_data['author']

            if search_type == 'adverts':
                results = (
                    Advert.objects.filter(Q(title__icontains=query) | Q(text__icontains=query))
                    .filter(author__username__icontains=author, is_published=True)
                )
            elif search_type == 'responses':
                results = (
                    Response.objects.filter(text__icontains=query)
                    .filter(author__username__icontains=author, is_accepted=True)
                )

        context = {
            'form': form,
            'results': results,
            'title': 'Поиск',
        }

        return render(request, self.template_name, context)


class SubscribeToCategoryView(LoginRequiredMixin, ListView):
    def post(self, request, cat_slug):
        category = get_object_or_404(Category, slug=cat_slug)
        subscription, created = Subscription.objects.get_or_create(user=request.user, category=category)

        if created:
            messages.success(request, f'Вы успешно подписались на категорию {category.name}')
        else:
            messages.info(request, f'Вы уже подписаны на категорию {category.name}')

        return redirect(category.get_absolute_url())


class UnsubscribeFromCategoryView(LoginRequiredMixin, ListView):
    def post(self, request, cat_slug):
        category = get_object_or_404(Category, slug=cat_slug)
        subscription = Subscription.objects.filter(user=request.user, category=category)

        if subscription.exists():
            subscription.delete()
            messages.success(request, f'Вы отписались от категории {category.name}')
        else:
            messages.info(request, f'Вы не подписаны на категорию {category.name}')

        return redirect(category.get_absolute_url())


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
