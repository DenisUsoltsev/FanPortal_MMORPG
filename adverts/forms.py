from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Advert, Response


class AddPostForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Категория не выбрана",
        label="Категории"
    )

    class Meta:
        model = Advert
        fields = ['title', 'text', 'is_published', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            # 'text': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError("Длина превышает 100 символов")
        return title


class AddResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={'cols': 100, 'rows': 7}),
        }


class SearchForm(forms.Form):
    CHOICES = [
        ('adverts', 'Объявление'),
        ('responses', 'Отклик'),
    ]

    search_type = forms.ChoiceField(choices=CHOICES, required=True, label="Что ищем?")
    query = forms.CharField(max_length=100, required=False, label="Текст поиска")
    author = forms.CharField(max_length=50, required=False, label="Автор")


class ResponseSearchForm(forms.Form):
    CHOICES = [
        ('user_responses', 'Отклики пользователя'),
        ('responses', 'Отклики на объявления пользователя'),
    ]

    search_type = forms.ChoiceField(choices=CHOICES, required=True, label='Что ищем?')
    #status = forms.ChoiceField(choices=Response.Status, required=True, label='Статус')
    title = forms.CharField(required=False, label='Заголовок объявления')
    content = forms.CharField(required=False, label='Содержимое отклика')
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Дата начала')
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Дата окончания')
