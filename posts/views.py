from rest_framework import generics, status, permissions, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Post, Like, Comment, CommentLike
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly, IsCommentOwnerOrPostOwner


# ------------------------------------------------------------
# Custom Pagination Classes
# ------------------------------------------------------------
class PostPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class CommentPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# ------------------------------------------------------------
# Post List & Create View (Authenticated only)
# ------------------------------------------------------------
class PostListCreateView(generics.ListCreateAPIView):
    """
    GET  -> list all posts (authenticated only)
    POST -> create new post (authenticated only)
    """
    queryset = Post.objects.all().select_related("author").prefetch_related("media", "likes", "comments")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]  # 👈 changed here
    pagination_class = PostPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ------------------------------------------------------------
# Post Detail, Update, Delete
# ------------------------------------------------------------
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    -> retrieve post details
    PUT    -> update post (author only)
    DELETE -> delete post (author only)
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]  # 👈 changed here


# ------------------------------------------------------------
# Retrieve Posts by User
# ------------------------------------------------------------
class UserPostsView(generics.ListAPIView):
    """
    GET -> list all posts by a specific user (authenticated only)
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]  # 👈 changed here
    pagination_class = PostPagination

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return (
            Post.objects.filter(author_id=user_id)
            .select_related("author")
            .prefetch_related("media", "likes", "comments")
        )


# ------------------------------------------------------------
# Like & Unlike Post
# ------------------------------------------------------------
class PostLikeToggleView(APIView):
    """
    POST -> toggle like/unlike a post
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user = request.user

        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()
            return Response({"message": "Unliked post"}, status=status.HTTP_200_OK)
        return Response({"message": "Liked post"}, status=status.HTTP_201_CREATED)


# ------------------------------------------------------------
# Create Comment on Post
# ------------------------------------------------------------
class CommentCreateView(APIView):
    """
    POST -> add comment or reply to a post
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(data=request.data, context={"request": request, "post": post})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------
# List Comments for a Post (Authenticated only)
# ------------------------------------------------------------
class CommentListView(generics.ListAPIView):
    """
    GET -> list comments for a specific post (authenticated only)
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]  # 👈 changed here
    pagination_class = CommentPagination

    def get_queryset(self):
        post_id = self.kwargs.get("pk")
        return Comment.objects.filter(post_id=post_id, parent_comment__isnull=True).select_related("author")


# ------------------------------------------------------------
# Delete Comment
# ------------------------------------------------------------
class CommentDeleteView(generics.DestroyAPIView):
    """
    DELETE -> delete a comment (only author or post owner)
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwnerOrPostOwner]  # 👈 changed here


# ------------------------------------------------------------
# Like & Unlike Comment
# ------------------------------------------------------------
class CommentLikeToggleView(APIView):
    """
    POST -> toggle like/unlike a comment
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        user = request.user

        like, created = CommentLike.objects.get_or_create(user=user, comment=comment)
        if not created:
            like.delete()
            return Response({"message": "Unliked comment"}, status=status.HTTP_200_OK)
        return Response({"message": "Liked comment"}, status=status.HTTP_201_CREATED)
