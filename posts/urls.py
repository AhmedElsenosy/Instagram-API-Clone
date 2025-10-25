from django.urls import path
from . import views

urlpatterns = [
    path("comments/<int:pk>/", views.CommentDeleteView.as_view(), name="delete-comment"),
    path("comments/<int:pk>/like/", views.CommentLikeToggleView.as_view(), name="like-comment"),

    # 📸 Posts
    path("", views.PostListCreateView.as_view(), name="post-list-create"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("user/<int:user_id>/", views.UserPostsView.as_view(), name="user-posts"),
    path("<int:pk>/like/", views.PostLikeToggleView.as_view(), name="post-like"),
    path("<int:pk>/comment/", views.CommentCreateView.as_view(), name="add-comment"),
    path("<int:pk>/comments/", views.CommentListView.as_view(), name="list-comments"),
]
