from django.urls import path
from .views import (
    PostsList, PostDetail, PostsSearchList, PostCreateView, PostUpdateView, PostDeleteView,
    ProfileView, upgrade_me,
)

urlpatterns = [
    path('', PostsList.as_view(), name='post_list'),
    path('<int:id>/', PostDetail.as_view(), name='post_detail'),
    path('search/', PostsSearchList.as_view(), name='post_search'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<int:id>/edit', PostUpdateView.as_view(), name='post_update'),
    path('<int:id>/delete', PostDeleteView.as_view(), name='post_delete'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/upgrade/', upgrade_me, name='upgrade'),
]