from django import forms
from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter
from .models import Post, Author


class PostFilter(FilterSet):
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название заголовка'
    )
    author = ModelChoiceFilter(
        queryset=Author.objects.all(),
        lookup_expr='exact',
        label='Автор',
        empty_label='Все авторы',
    )
    created_at = DateFilter(
        field_name='created_at',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form'}),
        lookup_expr='date__gte',
        label='Дата'
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'author',
            'created_at'
        ]