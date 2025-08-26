from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from .models import Post, Author, Category
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .filters import PostFilter
from .forms import PostForm





# Create your views here.
class PostsList(ListView):
    # model = Post
    # ordering = '-created_at'
    queryset = Post.objects.order_by('-created_at')
    template_name = 'posts.html'
    context_object_name = 'news'
    paginate_by = 10


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'news'
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            # return custom template
            return render(request, 'no_post.html', status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class PostsSearchList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'search.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_create_or_edit.html'
    # success_url = '/news/'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/articles/create/':
            post.post_type = 'AR'
        post.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_title'] = self.get_type()['title']
        context['get_type'] = self.get_type()['content']
        return context

    def get_type(self):
        if self.request.path == '/articles/create/':
            return {'title': 'Добавить статью', 'content': 'Добавление новой статьи'}
        else:
            return {'title': 'Добавить новость', 'content': 'Добавление новости'}


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_create_or_edit.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_title'] = self.get_type()['title']
        context['get_type'] = self.get_type()['content']
        return context

    def get_type(self):
        if 'articles' in self.request.path:
            return {'title': 'Изменить статью', 'content': 'Редактировать статью'}
        else:
            return {'title': 'Изменить новость', 'content': 'Редактировать новость'}


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    pk_url_kwarg = 'id'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        Author.objects.create(user_id=request.user.pk)
    return redirect('/news/profile/')

class CategoryListView(PostsList):
    model = Post
    template_name = 'news/category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.categories = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.categories).order_by('-datetime_post')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.categories.subscribers.all()
        context['category'] = self.categories
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    categories = Category.objects.get(id=pk)
    categories.subscribers.add(user)

    message = 'Вы успешно подписались на рассылку новых публикаций в категории: '
    return render(request, 'account/subscribe.html', {'category': categories, 'message': message})


@login_required
def unsubscribe(request, pk):
    user = request.user
    categories = Category.objects.get(id=pk)
    categories.subscribers.remove(user)

    message = 'Вы успешно отписаны от рассылки по категории: '
    return render(request, 'account/unsubscribe.html', {'category': categories, 'message': message})