from django.urls import path

from . import views
from .views import PostDeleteView, CommentCreateView, CommentDeleteView, \
    CommentEditView

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:id>/edit/', views.PostEditView.as_view(),
         name='edit_post'),
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),
    path('profile/<str:username>/edit/', views.EditProfileView.as_view(),
         name='edit_profile'),
    path('posts/<int:post_id>/comment/', CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/',
         CommentEditView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/',
         CommentDeleteView.as_view(), name='delete_comment'),
]
