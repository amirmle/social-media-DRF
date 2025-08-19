from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/comments/', views.PostCommentListView.as_view(), name='comment-list'),
    path('<int:post_id>/comments/<int:comment_id>/', views.PostCommentDetailView.as_view(), name='comment-detail'),
    path('<int:post_id>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('feed/', views.PostFeedView.as_view(), name='post-feed'),
]